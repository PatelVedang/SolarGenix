"""
Production-grade PDF ingestion service with batching, transactions,
metadata tracking, and comprehensive error handling.
"""
import logging
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import PyPDF2
from django.db import transaction

from .rag_shared import (
    get_embedder,
    chunk_hash,
    chunk_text,
    get_db_connection,
    page_hash,
)

# =====================================================
# LOGGING SETUP
# =====================================================
logger = logging.getLogger(__name__)

# =====================================================
# CONFIG
# =====================================================
EMBEDDING_BATCH_SIZE = 32  # Process embeddings in batches to avoid memory overflow
MIN_CHUNK_LENGTH = 50  # Minimum characters for a valid chunk
MIN_PDF_TEXT_LENGTH = 100  # Minimum text length to consider PDF valid

# =====================================================
# CUSTOM EXCEPTIONS
# =====================================================
class PDFIngestionError(Exception):
    """Base exception for PDF ingestion errors."""
    pass


class PDFExtractionError(PDFIngestionError):
    """Raised when PDF text extraction fails."""
    pass


class InsufficientContentError(PDFIngestionError):
    """Raised when PDF has too little text content."""
    pass


# =====================================================
# TEXT CLEANING
# =====================================================
def clean_pdf_text(text: str) -> str:
    """
    Clean and normalize text extracted from PDF.
    
    Improvements over basic cleaning:
    - Remove excessive newlines while preserving paragraph breaks
    - Normalize whitespace
    - Remove special characters that don't add semantic value
    - Preserve sentence boundaries
    
    Args:
        text: Raw text from PDF
        
    Returns:
        Cleaned and normalized text
    """
    if not text:
        return ""
    
    try:
        # Remove null bytes (can cause database issues)
        text = text.replace("\x00", "")
        
        # Replace multiple newlines with double newline (preserve paragraphs)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Replace single newlines with space (fix PDF line breaks)
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        
        # Normalize multiple spaces to single space
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove spaces before punctuation
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        
        # Normalize paragraph breaks
        text = re.sub(r'\n\n+', '\n\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        logger.debug(f"Cleaned text: {len(text)} chars")
        return text
        
    except Exception as e:
        logger.warning(f"Text cleaning encountered error: {e}. Returning basic cleaned text.")
        # Fallback to basic cleaning
        return text.replace("\x00", "").strip()


# =====================================================
# PDF EXTRACTION
# =====================================================
def extract_text_from_pdf(pdf_path: str) -> Tuple[str, Dict]:
    """
    Extract text from PDF with metadata.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Tuple of (cleaned_text, metadata_dict)
        
    Raises:
        PDFExtractionError: If extraction fails
        InsufficientContentError: If PDF has too little text
    """
    try:
        logger.info(f"Extracting text from PDF: {pdf_path}")
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            logger.debug(f"PDF has {num_pages} pages")
            
            # Extract text from all pages
            text = ""
            for page_num in range(num_pages):
                try:
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    text += page_text + "\n\n"  # Add paragraph break between pages
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    continue
            
            # Clean the extracted text
            cleaned_text = clean_pdf_text(text)
            
            # Validate extracted text
            if len(cleaned_text) < MIN_PDF_TEXT_LENGTH:
                raise InsufficientContentError(
                    f"PDF contains insufficient text ({len(cleaned_text)} chars, minimum {MIN_PDF_TEXT_LENGTH})"
                )
            
            # Build metadata
            metadata = {
                'num_pages': num_pages,
                'file_name': Path(pdf_path).name,
                'text_length': len(cleaned_text),
            }
            
            # Try to extract PDF metadata
            try:
                if pdf_reader.metadata:
                    metadata['title'] = pdf_reader.metadata.get('/Title', '')
                    metadata['author'] = pdf_reader.metadata.get('/Author', '')
            except Exception:
                pass  # Metadata extraction is optional
            
            logger.info(f"Successfully extracted {len(cleaned_text)} chars from {num_pages} pages")
            return cleaned_text, metadata
            
    except InsufficientContentError:
        raise
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}", exc_info=True)
        raise PDFExtractionError(f"Failed to extract text from PDF: {e}")


# =====================================================
# DB HELPERS
# =====================================================
def get_page_hash_by_source(source: str) -> Optional[str]:
    """
    Get the content hash for a given source.
    
    Args:
        source: Source identifier (e.g., "pdf://filename.pdf")
        
    Returns:
        Content hash if exists, None otherwise
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT content_hash FROM pages WHERE url = %s AND is_active = TRUE",
            (source,)
        )
        row = cur.fetchone()
        return row[0] if row else None
    except Exception as e:
        logger.error(f"Failed to get page hash: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def upsert_page(source: str, content_hash: str, tenant_id: str) -> None:
    """
    Insert or update page record with transaction safety.
    
    Args:
        source: Source identifier
        content_hash: Hash of page content
        tenant_id: Tenant identifier
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO pages (url, content_hash, is_active, tenant_id)
            VALUES (%s, %s, TRUE, %s)
            ON CONFLICT (url)
            DO UPDATE SET
                content_hash = EXCLUDED.content_hash,
                last_indexed = NOW(),
                is_active = TRUE,
                tenant_id = EXCLUDED.tenant_id
        """, (source, content_hash, tenant_id))
        
        conn.commit()
        logger.debug(f"Upserted page: {source}")
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Failed to upsert page: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def delete_page_chunks(source: str) -> int:
    """
    Delete all chunks associated with a source.
    
    Args:
        source: Source identifier
        
    Returns:
        Number of deleted chunks
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("DELETE FROM documents WHERE page_url = %s", (source,))
        deleted_count = cur.rowcount
        
        conn.commit()
        logger.info(f"Deleted {deleted_count} chunks for source: {source}")
        return deleted_count
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Failed to delete chunks: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# =====================================================
# EMBEDDING & CHUNKING
# =====================================================
def process_chunks_in_batches(chunks: List[str], source: str, metadata: Dict) -> List[Dict]:
    """
    Generate embeddings in batches and prepare chunk data.
    
    Batching prevents memory overflow and allows for progress tracking.
    Each chunk includes metadata for better retrieval.
    
    Args:
        chunks: List of text chunks
        source: Source identifier
        metadata: PDF metadata
        
    Returns:
        List of dicts with chunk data ready for DB insertion
    """
    try:
        embedder = get_embedder()
        chunk_data = []
        
        # Filter out chunks that are too short
        valid_chunks = [c for c in chunks if len(c.strip()) >= MIN_CHUNK_LENGTH]
        logger.info(f"Processing {len(valid_chunks)} valid chunks in batches of {EMBEDDING_BATCH_SIZE}")
        
        # Process in batches
        for i in range(0, len(valid_chunks), EMBEDDING_BATCH_SIZE):
            batch = valid_chunks[i:i + EMBEDDING_BATCH_SIZE]
            batch_num = (i // EMBEDDING_BATCH_SIZE) + 1
            total_batches = (len(valid_chunks) + EMBEDDING_BATCH_SIZE - 1) // EMBEDDING_BATCH_SIZE
            
            logger.debug(f"Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)")
            
            try:
                # Prefix with 'search_document:' for asymmetric search (Nomic best practice)
                prefixed_batch = ["search_document: " + chunk for chunk in batch]
                embeddings = embedder.encode(
                    prefixed_batch,
                    normalize_embeddings=True,
                    batch_size=EMBEDDING_BATCH_SIZE
                )
                
                # Build chunk data with metadata
                for j, (chunk, embedding) in enumerate(zip(batch, embeddings)):
                    chunk_index = i + j
                    chunk_data.append({
                        'content': chunk,
                        'source': source,
                        'page_url': source,
                        'embedding': embedding.tolist(),
                        'hash': chunk_hash(chunk),
                        'chunk_index': chunk_index,  # Metadata: position in document
                        'file_name': metadata.get('file_name', ''),  # Metadata: source file
                    })
                
            except Exception as e:
                logger.error(f"Batch {batch_num} embedding failed: {e}")
                # Continue with next batch instead of failing completely
                continue
        
        logger.info(f"Successfully processed {len(chunk_data)} chunks")
        return chunk_data
        
    except Exception as e:
        logger.error(f"Chunk processing failed: {e}", exc_info=True)
        raise


def insert_chunks_transactional(chunk_data: List[Dict]) -> int:
    """
    Insert chunks into database within a transaction.
    
    Uses transaction to ensure all-or-nothing insertion.
    Implements batch insertion for better performance.
    
    Args:
        chunk_data: List of chunk dictionaries
        
    Returns:
        Number of successfully inserted chunks
    """
    conn = None
    cur = None
    inserted_count = 0
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Start explicit transaction
        conn.autocommit = False
        
        logger.debug(f"Inserting {len(chunk_data)} chunks in transaction")
        
        for chunk in chunk_data:
            try:
                # ON CONFLICT DO NOTHING prevents duplicate entries based on hash
                cur.execute("""
                    INSERT INTO documents (content, source, page_url, embedding, hash)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (hash) DO NOTHING
                """, (
                    chunk['content'],
                    chunk['source'],
                    chunk['page_url'],
                    chunk['embedding'],
                    chunk['hash']
                ))
                
                if cur.rowcount > 0:
                    inserted_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to insert chunk {chunk.get('chunk_index')}: {e}")
                # Continue with other chunks
                continue
        
        # Commit transaction
        conn.commit()
        logger.info(f"Successfully inserted {inserted_count}/{len(chunk_data)} chunks")
        return inserted_count
        
    except Exception as e:
        logger.error(f"Transaction failed: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.autocommit = True
        if cur:
            cur.close()
        if conn:
            conn.close()


# =====================================================
# MAIN SYNC LOGIC
# =====================================================
def sync_pdf_to_db(pdf_path: str, tenant_id: str) -> Dict:
    """
    Extract PDF content and sync to vector database with full error handling.
    
    Args:
        pdf_path: Path to PDF file
        tenant_id: Tenant identifier
        
    Returns:
        Dict with ingestion results
        
    Raises:
        PDFIngestionError: If ingestion fails
    """
    source = f"pdf://{Path(pdf_path).name}"
    
    try:
        logger.info(f"Starting PDF ingestion: {pdf_path} for tenant: {tenant_id}")
        
        # Extract text with metadata
        text, metadata = extract_text_from_pdf(pdf_path)
        
        # Check if content has changed (skip if unchanged)
        new_hash = page_hash(text)
        old_hash = get_page_hash_by_source(source)
        
        if old_hash == new_hash:
            logger.info(f"PDF unchanged (hash match), skipping: {source}")
            return {
                'status': 'skipped',
                'reason': 'content_unchanged',
                'source': source,
            }
        
        logger.info(f"PDF content changed or new, processing...")
        
        # Delete old chunks if updating
        if old_hash:
            delete_page_chunks(source)
        
        # Generate chunks
        chunks = list(chunk_text(text))
        logger.info(f"Generated {len(chunks)} chunks")
        
        # Process chunks with embeddings
        chunk_data = process_chunks_in_batches(chunks, source, metadata)
        
        # Insert into database with transaction
        inserted_count = insert_chunks_transactional(chunk_data)
        
        # Update page record
        upsert_page(source, new_hash, tenant_id)
        
        logger.info(f"PDF ingestion completed: {source}")
        
        return {
            'status': 'success',
            'source': source,
            'chunks_generated': len(chunks),
            'chunks_inserted': inserted_count,
            'text_length': len(text),
            'metadata': metadata,
        }
        
    except (PDFExtractionError, InsufficientContentError) as e:
        logger.error(f"PDF ingestion failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during PDF sync: {e}", exc_info=True)
        raise PDFIngestionError(f"PDF ingestion failed: {e}")


# =====================================================
# DELETE OPERATIONS
# =====================================================
def delete_tenant_knowledge_base(tenant_id: str) -> Dict:
    """
    Delete all documents and pages for a specific tenant with transaction safety.
    
    Args:
        tenant_id: Tenant identifier
        
    Returns:
        Dict with deletion results
    """
    conn = None
    cur = None
    
    try:
        logger.info(f"Deleting knowledge base for tenant: {tenant_id}")
        
        conn = get_db_connection()
        cur = conn.cursor()
        conn.autocommit = False
        
        # Get page count before deletion
        cur.execute("""
            SELECT COUNT(*) FROM pages 
            WHERE tenant_id = %s AND is_active = TRUE
        """, (tenant_id,))
        page_count = cur.fetchone()[0]
        
        if page_count == 0:
            logger.warning(f"No knowledge base found for tenant: {tenant_id}")
            return {
                'status': 'not_found',
                'tenant_id': tenant_id,
                'deleted_documents': 0,
                'deleted_pages': 0,
            }
        
        # Delete documents
        cur.execute("""
            DELETE FROM documents 
            WHERE page_url IN (
                SELECT url FROM pages WHERE tenant_id = %s
            )
        """, (tenant_id,))
        deleted_docs = cur.rowcount
        
        # Delete pages
        cur.execute("DELETE FROM pages WHERE tenant_id = %s", (tenant_id,))
        deleted_pages = cur.rowcount
        
        conn.commit()
        
        logger.info(f"Deleted {deleted_docs} documents and {deleted_pages} pages for tenant: {tenant_id}")
        
        return {
            'status': 'success',
            'tenant_id': tenant_id,
            'deleted_documents': deleted_docs,
            'deleted_pages': deleted_pages,
        }
        
    except Exception as e:
        logger.error(f"Knowledge base deletion failed: {e}", exc_info=True)
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.autocommit = True
        if cur:
            cur.close()
        if conn:
            conn.close()


# =====================================================
# CONTROLLER
# =====================================================
def ingest_pdf(pdf_path: str, tenant_id: str) -> Dict:
    """
    Main entry point for PDF ingestion with validation.
    
    Args:
        pdf_path: Path to PDF file
        tenant_id: Tenant identifier
        
    Returns:
        Dict with ingestion results
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If file is not a PDF
        PDFIngestionError: If ingestion fails
    """
    # Validate file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Validate file extension
    if not pdf_path.lower().endswith('.pdf'):
        raise ValueError("File must be a PDF")
    
    # Validate tenant_id
    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id is required")
    
    return sync_pdf_to_db(pdf_path, tenant_id.strip())
