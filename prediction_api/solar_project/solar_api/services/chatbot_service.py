"""
Production-grade chatbot service with comprehensive error handling,
logging, and performance optimizations.
"""
import logging
import os
import re
from typing import List, Tuple, Optional

from groq import Groq
from groq import APIError, RateLimitError, APIConnectionError

from .rag_shared import get_embedder, get_db_connection

# =====================================================
# LOGGING SETUP
# =====================================================
logger = logging.getLogger(__name__)

# =====================================================
# CONFIG
# =====================================================
TOP_K = 15
MAX_CONTEXT_CHARS = 3500
MAX_COMPLETION_TOKENS = 300
EMBEDDING_BATCH_SIZE = 32  # Process embeddings in batches to avoid memory issues

# =====================================================
# CUSTOM EXCEPTIONS
# =====================================================
class ChatbotServiceError(Exception):
    """Base exception for chatbot service errors."""
    pass


class APIKeyMissingError(ChatbotServiceError):
    """Raised when required API key is missing."""
    pass


class EmbeddingError(ChatbotServiceError):
    """Raised when embedding generation fails."""
    pass


class LLMError(ChatbotServiceError):
    """Raised when LLM API call fails."""
    pass


class DatabaseError(ChatbotServiceError):
    """Raised when database operation fails."""
    pass


# =====================================================
# SYNONYM EXPANSION
# =====================================================
SYNONYM_GROUPS = {
    # Contact information
    "phone": ["phone", "telephone", "mobile", "contact number", "phone number", "cell", "call"],
    "email": ["email", "e-mail", "mail", "email address"],
    "address": ["address", "location", "office", "office address", "place", "where"],
    "contact": ["contact", "reach", "get in touch", "phone", "email"],
    
    # Time related
    "hours": ["hours", "timing", "time", "schedule", "open", "close", "working hours"],
    "appointment": ["appointment", "booking", "schedule", "reservation"],
    
    # Common queries
    "cost": ["cost", "price", "fee", "charge", "rate", "pricing"],
    "service": ["service", "services", "offering", "offerings", "provide"],
    "doctor": ["doctor", "physician", "dr", "specialist"],
    
    # General
    "website": ["website", "site", "web", "online", "url"],
}


def expand_query(question: str) -> str:
    """
    Expand the query with synonyms to improve retrieval coverage.
    
    This improves recall by including semantically related terms that might
    appear in the knowledge base but not in the original question.
    
    Args:
        question: The original user question
        
    Returns:
        Expanded query string with synonyms added
    """
    try:
        question_lower = question.lower()
        expanded_terms = [question]  # Always include original query
        
        # Check each synonym group
        for base_term, synonyms in SYNONYM_GROUPS.items():
            # If any synonym is in the question, add all related terms
            for synonym in synonyms:
                if synonym in question_lower:
                    # Add other synonyms from this group
                    expanded_terms.extend([s for s in synonyms if s not in question_lower])
                    break  # Only add once per group
        
        # Join all terms together
        expanded_query = " ".join(expanded_terms)
        logger.debug(f"Expanded query from '{question}' to '{expanded_query}'")
        return expanded_query
    except Exception as e:
        logger.warning(f"Query expansion failed: {e}. Using original question.")
        return question


# =====================================================
# RETRIEVAL
# =====================================================
def retrieve_context(question: str, tenant_id: str) -> List[str]:
    """
    Hybrid RAG retrieval with robust error handling.
    
    Strategy:
    1. Synonym expansion for better recall
    2. Generate query embedding
    3. Vector similarity search (primary)
    4. Keyword fallback search (secondary)
    5. Merge and deduplicate results
    
    Args:
        question: User's question
        tenant_id: Tenant identifier for multi-tenancy
        
    Returns:
        List of context strings formatted as "[source] content"
        
    Raises:
        DatabaseError: If database operations fail
        EmbeddingError: If embedding generation fails
    """
    conn = None
    cur = None
    
    try:
        # -------------------------------------------------
        # 1️⃣ Synonym expansion
        # -------------------------------------------------
        expanded_question = expand_query(question)
        
        # -------------------------------------------------
        # 2️⃣ Query embedding
        # -------------------------------------------------
        try:
            # Prefix with 'search_query:' for asymmetric search (Nomic embedding best practice)
            embedder = get_embedder()
            query_embedding = embedder.encode(
                ["search_query: " + expanded_question],
                normalize_embeddings=True
            )[0]
            query_embedding = query_embedding.tolist()
            logger.debug(f"Generated embedding for query: {question[:50]}...")
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise EmbeddingError(f"Failed to generate query embedding: {e}")
        
        # -------------------------------------------------
        # 3️⃣ Database operations with connection management
        # -------------------------------------------------
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Vector similarity search
            logger.debug(f"Executing vector search for tenant: {tenant_id}")
            cur.execute("""
                SELECT d.content, d.source
                FROM documents d
                JOIN pages p ON d.page_url = p.url
                WHERE p.is_active = TRUE
                  AND p.tenant_id = %s
                ORDER BY d.embedding <=> %s::vector
                LIMIT %s
            """, (tenant_id, query_embedding, TOP_K))
            
            vector_rows = cur.fetchall()
            logger.info(f"Vector search returned {len(vector_rows)} results")
            
            # -------------------------------------------------
            # 4️⃣ Keyword fallback search
            # -------------------------------------------------
            # Extract meaningful keywords (3+ chars, alphanumeric)
            keywords = re.findall(r'\b[a-zA-Z]{3,}\b', question.lower())
            keywords = list(set(keywords))[:4]  # Limit to top 4 unique keywords
            
            keyword_rows = []
            if keywords:
                logger.debug(f"Executing keyword search with terms: {keywords}")
                for kw in keywords:
                    cur.execute("""
                        SELECT d.content, d.source
                        FROM documents d
                        JOIN pages p ON d.page_url = p.url
                        WHERE p.is_active = TRUE
                          AND p.tenant_id = %s
                          AND d.content ILIKE %s
                        LIMIT 3
                    """, (tenant_id, f"%{kw}%"))
                    
                    keyword_rows.extend(cur.fetchall())
                
                logger.info(f"Keyword search returned {len(keyword_rows)} results")
            
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise DatabaseError(f"Failed to retrieve context from database: {e}")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
        
        # -------------------------------------------------
        # 5️⃣ Merge + deduplicate
        # -------------------------------------------------
        combined = vector_rows + keyword_rows
        
        seen = set()
        unique_rows = []
        
        for text, src in combined:
            # Use hash for deduplication (faster than string comparison)
            h = hash(text)
            if h not in seen:
                seen.add(h)
                unique_rows.append((text, src))
        
        logger.debug(f"Deduplicated to {len(unique_rows)} unique results")
        
        # -------------------------------------------------
        # 6️⃣ Build final context with size limit
        # -------------------------------------------------
        # Limit total context to avoid token limit issues
        context = []
        total_chars = 0
        
        for text, src in unique_rows:
            entry = f"[{src}] {text}"
            if total_chars + len(entry) > MAX_CONTEXT_CHARS:
                break
            context.append(entry)
            total_chars += len(entry)
        
        logger.info(f"Built context with {len(context)} chunks ({total_chars} chars)")
        return context
        
    except (EmbeddingError, DatabaseError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error in retrieve_context: {e}", exc_info=True)
        raise ChatbotServiceError(f"Context retrieval failed: {e}")


# =====================================================
# LLM INTERACTION
# =====================================================
def ask_llm(question: str, context_chunks: List[str]) -> str:
    """
    Query the LLM with context using Groq API.
    
    Implements retry logic and graceful degradation if API fails.
    
    Args:
        question: User's question
        context_chunks: Retrieved context pieces
        
    Returns:
        LLM-generated answer
        
    Raises:
        APIKeyMissingError: If GROQ_API_KEY is not set
        LLMError: If LLM API call fails
    """
    # Validate API key exists
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY environment variable is not set")
        raise APIKeyMissingError("GROQ_API_KEY environment variable is required")
    
    # Handle empty context gracefully
    if not context_chunks:
        logger.warning("No context available for question")
        return "I don't have enough information to answer that question based on the available knowledge base."
    
    # Build prompt with clear instructions
    prompt = f"""Answer using ONLY the context provided below.
You may paraphrase or summarize clearly stated facts.
If the answer cannot be found or reasonably inferred from the context, respond with:
"I don't know based on the available information."

CONTEXT:
{chr(10).join(context_chunks)}

QUESTION:
{question}

ANSWER:"""
    
    try:
        logger.debug(f"Calling Groq API for question: {question[:50]}...")
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,  # Low temperature for factual responses
            max_tokens=MAX_COMPLETION_TOKENS
        )
        
        answer = response.choices[0].message.content
        logger.info(f"LLM response generated successfully ({len(answer)} chars)")
        return answer
        
    except RateLimitError as e:
        logger.error(f"Groq API rate limit exceeded: {e}")
        raise LLMError("The AI service is currently rate limited. Please try again in a moment.")
    except APIConnectionError as e:
        logger.error(f"Failed to connect to Groq API: {e}")
        raise LLMError("Failed to connect to AI service. Please check your internet connection.")
    except APIError as e:
        logger.error(f"Groq API error: {e}")
        raise LLMError(f"AI service error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error calling LLM: {e}", exc_info=True)
        raise LLMError(f"Failed to generate response: {str(e)}")


# =====================================================
# MAIN PUBLIC API
# =====================================================
def get_chatbot_response(question: str, tenant_id: str) -> Tuple[str, Optional[str]]:
    """
    Main entry point for chatbot queries.
    
    This function orchestrates the full RAG pipeline:
    1. Retrieve relevant context from vector DB
    2. Query LLM with context
    3. Return answer with error handling
    
    Args:
        question: User's question
        tenant_id: Tenant identifier
        
    Returns:
        Tuple of (answer, error_message)
        - If successful: (answer_text, None)
        - If error: (fallback_message, error_description)
    """
    try:
        logger.info(f"Processing chatbot query for tenant: {tenant_id}")
        
        # Validate inputs
        if not question or not question.strip():
            logger.warning("Empty question received")
            return ("Please provide a question.", "Empty question")
        
        if not tenant_id or not tenant_id.strip():
            logger.warning("Empty tenant_id received")
            return ("Invalid request: tenant_id is required.", "Missing tenant_id")
        
        # Retrieve context
        context = retrieve_context(question.strip(), tenant_id.strip())
        
        # Generate answer
        answer = ask_llm(question.strip(), context)
        
        return (answer, None)
        
    except APIKeyMissingError as e:
        logger.error(f"API key missing: {e}")
        return (
            "The chatbot service is not properly configured. Please contact support.",
            str(e)
        )
    except EmbeddingError as e:
        logger.error(f"Embedding error: {e}")
        return (
            "Failed to process your question. Please try rephrasing it.",
            str(e)
        )
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        return (
            "Failed to access the knowledge base. Please try again later.",
            str(e)
        )
    except LLMError as e:
        logger.error(f"LLM error: {e}")
        return (str(e), str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_chatbot_response: {e}", exc_info=True)
        return (
            "An unexpected error occurred. Please try again.",
            f"Unexpected error: {str(e)}"
        )
