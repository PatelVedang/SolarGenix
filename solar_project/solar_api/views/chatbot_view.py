"""
Production-grade Django REST Framework views with comprehensive error handling,
validation, logging, and proper HTTP status codes.
"""
import logging
import os
from typing import Any, Dict

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from solar_api.services.chatbot_service import (
    get_chatbot_response,
    APIKeyMissingError,
    EmbeddingError,
    DatabaseError,
    LLMError,
)
from solar_api.services.pdf_ingestion_service import (
    ingest_pdf,
    delete_tenant_knowledge_base,
    PDFExtractionError,
    InsufficientContentError,
    PDFIngestionError,
)

# =====================================================
# LOGGING SETUP
# =====================================================
logger = logging.getLogger(__name__)

# =====================================================
# VALIDATION HELPERS
# =====================================================
def validate_pdf_file(pdf_file: Any) -> Dict[str, Any]:
    """
    Validate uploaded PDF file.
    
    Args:
        pdf_file: Uploaded file object
        
    Returns:
        Dict with validation result
    """
    if not pdf_file:
        return {'valid': False, 'error': 'PDF file is required'}
    
    # Check file extension
    if not pdf_file.name.lower().endswith('.pdf'):
        return {'valid': False, 'error': 'File must be a PDF'}
    
    # Check file size (limit to 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if pdf_file.size > max_size:
        return {'valid': False, 'error': f'File size exceeds maximum of {max_size / 1024 / 1024}MB'}
    
    return {'valid': True}


def validate_tenant_id(tenant_id: str) -> Dict[str, Any]:
    """
    Validate tenant_id parameter.
    
    Args:
        tenant_id: Tenant identifier
        
    Returns:
        Dict with validation result
    """
    if not tenant_id:
        return {'valid': False, 'error': 'tenant_id is required'}
    
    if not tenant_id.strip():
        return {'valid': False, 'error': 'tenant_id cannot be empty'}
    
    # Additional validation: alphanumeric + underscore/hyphen only
    if not all(c.isalnum() or c in ('_', '-') for c in tenant_id):
        return {'valid': False, 'error': 'tenant_id can only contain letters, numbers, underscores, and hyphens'}
    
    return {'valid': True}


def validate_question(question: str) -> Dict[str, Any]:
    """
    Validate question parameter.
    
    Args:
        question: User's question
        
    Returns:
        Dict with validation result
    """
    if not question:
        return {'valid': False, 'error': 'question is required'}
    
    if not question.strip():
        return {'valid': False, 'error': 'question cannot be empty'}
    
    # Check length limits
    if len(question) > 1000:
        return {'valid': False, 'error': 'question exceeds maximum length of 1000 characters'}
    
    if len(question.strip()) < 3:
        return {'valid': False, 'error': 'question must be at least 3 characters'}
    
    return {'valid': True}


# =====================================================
# API VIEWS
# =====================================================
class PDFIngestionAPIView(APIView):
    """
    Production-grade API endpoint for PDF ingestion.
    
    Features:
    - Input validation with clear error messages
    - Proper error handling with appropriate HTTP status codes
    - Structured logging for debugging
    - Temporary file cleanup
    - Transaction safety
    """
    parser_classes = [MultiPartParser, FormParser]
    
    @swagger_auto_schema(
        operation_description="""Upload a PDF file to ingest its content into the vector database.
        
The PDF will be:
1. Validated for format and size
2. Text extracted and cleaned
3. Chunked with metadata
4. Embedded in batches
5. Stored in vector database

Maximum file size: 10MB
Supported format: PDF only""",
        manual_parameters=[
            openapi.Parameter(
                'pdf_file',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='PDF file to upload and ingest (max 10MB)'
            ),
            openapi.Parameter(
                'tenant_id',
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
                description='Tenant identifier (alphanumeric, underscores, hyphens only)'
            ),
        ],
        responses={
            200: openapi.Response(
                description='PDF ingested successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'file_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'tenant_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'chunks_generated': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'chunks_inserted': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'text_length': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            ),
            400: openapi.Response(
                description='Bad request - validation failed',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING),
                        'details': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            422: openapi.Response(
                description='Unprocessable entity - PDF content issues',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            500: openapi.Response(description='Internal server error'),
        },
        tags=['PDF Ingestion']
    )
    def post(self, request):
        """Handle PDF upload and ingestion."""
        temp_file_path = None
        
        try:
            # Extract parameters
            pdf_file = request.FILES.get('pdf_file')
            tenant_id = request.data.get('tenant_id')
            
            logger.info(f"PDF ingestion request for tenant: {tenant_id}")
            
            # Validate tenant_id
            tenant_validation = validate_tenant_id(tenant_id)
            if not tenant_validation['valid']:
                logger.warning(f"Tenant validation failed: {tenant_validation['error']}")
                return Response(
                    {
                        'error': tenant_validation['error'],
                        'field': 'tenant_id'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate PDF file
            file_validation = validate_pdf_file(pdf_file)
            if not file_validation['valid']:
                logger.warning(f"File validation failed: {file_validation['error']}")
                return Response(
                    {
                        'error': file_validation['error'],
                        'field': 'pdf_file'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                # Save uploaded file temporarily
                file_path = default_storage.save(
                    f'temp_pdfs/{pdf_file.name}',
                    ContentFile(pdf_file.read())
                )
                temp_file_path = default_storage.path(file_path)
                logger.debug(f"Temporary file saved: {temp_file_path}")
                
            except Exception as e:
                logger.error(f"Failed to save uploaded file: {e}")
                return Response(
                    {'error': 'Failed to process uploaded file', 'details': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            try:
                # Ingest PDF
                result = ingest_pdf(temp_file_path, tenant_id)
                
                # Handle skipped case (unchanged content)
                if result.get('status') == 'skipped':
                    logger.info(f"PDF skipped (unchanged): {pdf_file.name}")
                    return Response(
                        {
                            'message': 'PDF already ingested with same content (skipped)',
                            'file_name': pdf_file.name,
                            'tenant_id': tenant_id,
                            'status': 'skipped'
                        },
                        status=status.HTTP_200_OK
                    )
                
                # Success response
                logger.info(f"PDF ingestion successful: {pdf_file.name}")
                return Response(
                    {
                        'message': 'PDF ingested successfully',
                        'file_name': pdf_file.name,
                        'tenant_id': tenant_id,
                        'chunks_generated': result.get('chunks_generated', 0),
                        'chunks_inserted': result.get('chunks_inserted', 0),
                        'text_length': result.get('text_length', 0),
                    },
                    status=status.HTTP_200_OK
                )
                
            except InsufficientContentError as e:
                # PDF doesn't have enough text - HTTP 422 (Unprocessable Entity)
                logger.warning(f"PDF has insufficient content: {e}")
                return Response(
                    {'error': 'PDF contains insufficient text content', 'details': str(e)},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
                
            except PDFExtractionError as e:
                # PDF extraction failed - HTTP 422
                logger.error(f"PDF extraction failed: {e}")
                return Response(
                    {'error': 'Failed to extract text from PDF', 'details': str(e)},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
                
            except PDFIngestionError as e:
                # General ingestion error - HTTP 500
                logger.error(f"PDF ingestion error: {e}")
                return Response(
                    {'error': 'PDF ingestion failed', 'details': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error in PDF ingestion: {e}", exc_info=True)
            return Response(
                {'error': 'An unexpected error occurred', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        finally:
            # Always clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    # Try to remove directory if empty
                    try:
                        os.rmdir(os.path.dirname(temp_file_path))
                    except OSError:
                        pass
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file: {e}")


class ChatbotAPIView(APIView):
    """
    Production-grade chatbot API with comprehensive error handling.
    
    Features:
    - Input validation
    - Graceful error handling with user-friendly messages
    - Structured logging
    - Proper HTTP status codes
    - API key validation
    """
    parser_classes = [JSONParser]
    
    @swagger_auto_schema(
        operation_description="""Query the chatbot with a question.
        
The system will:
1. Validate input
2. Expand query with synonyms
3. Retrieve relevant context via hybrid search (vector + keyword)
4. Generate answer using LLM (Groq)

Note: Requires GROQ_API_KEY environment variable to be set.""",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['question', 'tenant_id'],
            properties={
                'question': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The question to ask (3-1000 characters)',
                    min_length=3,
                    max_length=1000
                ),
                'tenant_id': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Tenant identifier (alphanumeric, underscores, hyphens only)'
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description='Chatbot response generated successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'question': openapi.Schema(type=openapi.TYPE_STRING),
                        'answer': openapi.Schema(type=openapi.TYPE_STRING),
                        'tenant_id': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(
                description='Bad request - validation failed',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING),
                        'field': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            503: openapi.Response(
                description='Service unavailable - external API issues',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            500: openapi.Response(description='Internal server error'),
        },
        tags=['Chatbot']
    )
    def post(self, request):
        """Handle chatbot query."""
        try:
            # Extract parameters
            question = request.data.get('question')
            tenant_id = request.data.get('tenant_id')
            
            logger.info(f"Chatbot query for tenant: {tenant_id}")
            
            # Validate question
            question_validation = validate_question(question)
            if not question_validation['valid']:
                logger.warning(f"Question validation failed: {question_validation['error']}")
                return Response(
                    {
                        'error': question_validation['error'],
                        'field': 'question'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate tenant_id
            tenant_validation = validate_tenant_id(tenant_id)
            if not tenant_validation['valid']:
                logger.warning(f"Tenant validation failed: {tenant_validation['error']}")
                return Response(
                    {
                        'error': tenant_validation['error'],
                        'field': 'tenant_id'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                # Get chatbot response
                answer, error = get_chatbot_response(question, tenant_id)
                
                # Check if there was an internal error
                if error:
                    logger.warning(f"Chatbot service returned error: {error}")
                    # Still return 200 with user-friendly message
                    # The service already provides a good user-facing message
                
                return Response(
                    {
                        'question': question,
                        'answer': answer,
                        'tenant_id': tenant_id,
                    },
                    status=status.HTTP_200_OK
                )
                
            except APIKeyMissingError as e:
                # Configuration error - HTTP 503
                logger.error(f"API key missing: {e}")
                return Response(
                    {'error': 'Chatbot service is not properly configured. Please contact support.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
                
            except (EmbeddingError, DatabaseError) as e:
                # Internal service errors - HTTP 500
                logger.error(f"Service error: {e}")
                return Response(
                    {'error': 'An internal error occurred processing your request.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
            except LLMError as e:
                # External API error - HTTP 503
                logger.error(f"LLM API error: {e}")
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
                
        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error in chatbot endpoint: {e}", exc_info=True)
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteKnowledgeBaseAPIView(APIView):
    """
    Production-grade knowledge base deletion API.
    
    Features:
    - Input validation
    - Transaction safety
    - Comprehensive logging
    - Clear status reporting
    """
    parser_classes = [JSONParser]
    
    @swagger_auto_schema(
        operation_description="""Delete all knowledge base data for a specific tenant.
        
⚠️ WARNING: This operation is irreversible!

The operation will:
1. Validate tenant_id
2. Delete all associated documents
3. Delete all associated pages
4. Commit changes in a transaction

Returns details about deleted items.""",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['tenant_id'],
            properties={
                'tenant_id': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Tenant identifier for which to delete all knowledge base data'
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description='Knowledge base deleted successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'tenant_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'deleted_documents': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'deleted_pages': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(description='Bad request - missing or invalid tenant_id'),
            404: openapi.Response(description='No knowledge base found for tenant'),
            500: openapi.Response(description='Internal server error'),
        },
        tags=['Knowledge Base Management']
    )
    def delete(self, request):
        """Handle knowledge base deletion."""
        try:
            # Extract tenant_id
            tenant_id = request.data.get('tenant_id')
            
            logger.info(f"Knowledge base deletion request for tenant: {tenant_id}")
            
            # Validate tenant_id
            tenant_validation = validate_tenant_id(tenant_id)
            if not tenant_validation['valid']:
                logger.warning(f"Tenant validation failed: {tenant_validation['error']}")
                return Response(
                    {
                        'error': tenant_validation['error'],
                        'field': 'tenant_id'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                # Delete knowledge base
                result = delete_tenant_knowledge_base(tenant_id)
                
                # Handle not found case
                if result.get('status') == 'not_found':
                    logger.warning(f"No knowledge base found for tenant: {tenant_id}")
                    return Response(
                        {
                            'message': f'No knowledge base found for tenant: {tenant_id}',
                            'tenant_id': tenant_id,
                            'status': 'not_found'
                        },
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Success response
                logger.info(f"Knowledge base deleted for tenant: {tenant_id}")
                return Response(
                    {
                        'message': f'Knowledge base deleted successfully for tenant: {tenant_id}',
                        'tenant_id': tenant_id,
                        'deleted_documents': result.get('deleted_documents', 0),
                        'deleted_pages': result.get('deleted_pages', 0),
                        'status': 'success'
                    },
                    status=status.HTTP_200_OK
                )
                
            except Exception as e:
                logger.error(f"Knowledge base deletion failed: {e}", exc_info=True)
                return Response(
                    {'error': 'Failed to delete knowledge base', 'details': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Unexpected error in delete endpoint: {e}", exc_info=True)
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
