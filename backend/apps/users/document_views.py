"""
Document Summarizer API Views
Handles PDF/DOCX file upload and AI-powered summarization
"""

import logging
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.files.storage import default_storage
from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination

from .models import DocumentSummary
from .feature_serializers import (
    DocumentSummarySerializer, DocumentSummaryListSerializer,
    DocumentUploadSerializer, DocumentSummaryUpdateSerializer,
    DocumentSearchSerializer
)
from .document_utils import process_document

logger = logging.getLogger(__name__)

class DocumentSummaryPagination(PageNumberPagination):
    """Pagination for document summaries"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


# ============ DOCUMENT UPLOAD AND PROCESSING ============

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_document(request):
    """Upload and process a PDF/DOCX document for summarization"""
    try:
        logger.info(f"Document upload request from user: {request.user.email}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Content type: {request.content_type}")
        logger.info(f"Request data keys: {list(request.data.keys()) if hasattr(request, 'data') else 'No data'}")
        logger.info(f"Request FILES keys: {list(request.FILES.keys()) if hasattr(request, 'FILES') else 'No FILES'}")
        
        # Validate upload data
        logger.info(f"Validating upload data...")
        logger.info(f"Raw request data: {dict(request.data)}")
        
        serializer = DocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Upload validation failed: {serializer.errors}")
            logger.error(f"Received data: {request.data}")
            return Response(
                {'error': 'Invalid upload data', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = serializer.validated_data['file']
        title = serializer.validated_data.get('title', '')
        subject = serializer.validated_data.get('subject', '')
        tags = serializer.validated_data.get('tags', [])
        notes = serializer.validated_data.get('notes', '')
        
        # Create initial document summary record
        document_summary = DocumentSummary.objects.create(
            user=request.user,
            original_filename=uploaded_file.name,
            file_type='pdf' if uploaded_file.name.lower().endswith('.pdf') else 'docx',
            file_size=uploaded_file.size,
            title=title or uploaded_file.name,
            subject=subject,
            tags=tags,
            notes=notes,
            status='processing'
        )
        
        logger.info(f"Created document summary record with ID: {document_summary.id}")
        
        # Read file content
        file_content = uploaded_file.read()
        
        # Process document and generate summary
        try:
            logger.info(f"Starting document processing for: {uploaded_file.name}")
            logger.info(f"File size: {len(file_content)} bytes")
            
            result = process_document(file_content, uploaded_file.name)
            logger.info(f"Processing result: {result.get('success')}, Error: {result.get('error', 'None')}")
            
            if result['success']:
                # Update document with successful processing results
                document_summary.status = 'completed'
                document_summary.extracted_text = result['extracted_text']
                document_summary.summary = result['summary']
                document_summary.summary_metadata = result['metadata']
                document_summary.processing_error = ''
                
                # Optionally save the file (if you want to store it)
                # document_summary.uploaded_file.save(
                #     uploaded_file.name,
                #     uploaded_file,
                #     save=False
                # )
                
                logger.info(f"Successfully processed document {document_summary.id}")
                
            else:
                # Mark as failed and store error
                document_summary.status = 'failed'
                document_summary.processing_error = result['error']
                logger.error(f"Document processing failed for {document_summary.id}: {result['error']}")
            
            document_summary.save()
            
            # Return the processed document
            response_serializer = DocumentSummarySerializer(document_summary)
            
            return Response({
                'message': 'Document processed successfully' if result['success'] else 'Document processing failed',
                'document': response_serializer.data,
                'success': result['success']
            }, status=status.HTTP_201_CREATED if result['success'] else status.HTTP_400_BAD_REQUEST)
            
        except Exception as processing_error:
            logger.error(f"Unexpected processing error: {processing_error}")
            
            # Update document with error status
            document_summary.status = 'failed'
            document_summary.processing_error = f"Processing failed: {str(processing_error)}"
            document_summary.save()
            
            return Response(
                {
                    'error': 'Document processing failed',
                    'message': str(processing_error),
                    'document_id': document_summary.id
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Upload endpoint error: {e}")
        return Response(
            {'error': 'Upload failed', 'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============ DOCUMENT SUMMARY MANAGEMENT ============

class DocumentSummaryListView(generics.ListAPIView):
    """List user's document summaries with search and filtering"""
    
    serializer_class = DocumentSummaryListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DocumentSummaryPagination
    
    def get_queryset(self):
        queryset = DocumentSummary.objects.filter(user=self.request.user)
        
        # Apply search and filters
        query_params = self.request.query_params
        
        # Text search
        search_query = query_params.get('query', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(original_filename__icontains=search_query) |
                Q(extracted_text__icontains=search_query) |
                Q(summary__icontains=search_query) |
                Q(tags__contains=[search_query])
            )
        
        # File type filter
        file_type = query_params.get('file_type')
        if file_type and file_type != 'all':
            queryset = queryset.filter(file_type=file_type)
        
        # Status filter
        status_filter = query_params.get('status')
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        # Subject filter
        subject = query_params.get('subject')
        if subject:
            queryset = queryset.filter(subject__icontains=subject)
        
        # Favorites filter
        is_favorite = query_params.get('is_favorite')
        if is_favorite is not None:
            queryset = queryset.filter(is_favorite=is_favorite.lower() == 'true')
        
        # Ordering
        order_by = query_params.get('order_by', '-created_at')
        if order_by in ['-created_at', 'created_at', 'title', '-title', '-view_count']:
            queryset = queryset.order_by(order_by)
        
        return queryset


class DocumentSummaryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a document summary"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DocumentSummary.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DocumentSummaryUpdateSerializer
        return DocumentSummarySerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve document summary and update view count"""
        instance = self.get_object()
        instance.update_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_favorite(request, document_id):
    """Toggle favorite status of a document summary"""
    try:
        document = get_object_or_404(
            DocumentSummary,
            id=document_id,
            user=request.user
        )
        
        document.is_favorite = not document.is_favorite
        document.save(update_fields=['is_favorite'])
        
        return Response({
            'message': f'Document {"added to" if document.is_favorite else "removed from"} favorites',
            'is_favorite': document.is_favorite
        })
        
    except Exception as e:
        logger.error(f"Toggle favorite error: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def regenerate_summary(request, document_id):
    """Regenerate summary for an existing document"""
    try:
        document = get_object_or_404(
            DocumentSummary,
            id=document_id,
            user=request.user
        )
        
        if not document.extracted_text:
            return Response(
                {'error': 'No extracted text available for regeneration'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Import here to avoid circular imports
        from .document_utils import document_processor
        
        # Regenerate summary
        success, summary, metadata = document_processor.generate_summary(document.extracted_text)
        
        if success:
            document.summary = summary
            document.summary_metadata = metadata
            document.save(update_fields=['summary', 'summary_metadata'])
            
            serializer = DocumentSummarySerializer(document)
            return Response({
                'message': 'Summary regenerated successfully',
                'document': serializer.data
            })
        else:
            return Response(
                {'error': metadata.get('error', 'Failed to regenerate summary')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Regenerate summary error: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============ DASHBOARD AND STATISTICS ============

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def document_dashboard(request):
    """Get dashboard statistics for document summaries"""
    try:
        user_documents = DocumentSummary.objects.filter(user=request.user)
        
        # Basic statistics
        total_documents = user_documents.count()
        completed_documents = user_documents.filter(status='completed').count()
        processing_documents = user_documents.filter(status='processing').count()
        failed_documents = user_documents.filter(status='failed').count()
        favorite_documents = user_documents.filter(is_favorite=True).count()
        
        # File type breakdown
        pdf_count = user_documents.filter(file_type='pdf').count()
        docx_count = user_documents.filter(file_type='docx').count()
        
        # Recent documents (last 5)
        recent_documents = user_documents.order_by('-created_at')[:5]
        recent_serializer = DocumentSummaryListSerializer(recent_documents, many=True)
        
        # Most viewed documents
        popular_documents = user_documents.filter(
            view_count__gt=0
        ).order_by('-view_count')[:5]
        popular_serializer = DocumentSummaryListSerializer(popular_documents, many=True)
        
        # Calculate total words processed
        total_words = sum(doc.word_count for doc in user_documents.filter(status='completed'))
        
        return Response({
            'statistics': {
                'total_documents': total_documents,
                'completed_documents': completed_documents,
                'processing_documents': processing_documents,
                'failed_documents': failed_documents,
                'favorite_documents': favorite_documents,
                'pdf_count': pdf_count,
                'docx_count': docx_count,
                'total_words_processed': total_words,
                'success_rate': round(
                    (completed_documents / total_documents * 100) if total_documents > 0 else 0, 1
                )
            },
            'recent_documents': recent_serializer.data,
            'popular_documents': popular_serializer.data
        })
        
    except Exception as e:
        logger.error(f"Document dashboard error: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============ BATCH OPERATIONS ============

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_delete(request):
    """Bulk delete document summaries"""
    try:
        document_ids = request.data.get('document_ids', [])
        
        if not document_ids:
            return Response(
                {'error': 'No document IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Ensure user owns all documents
        documents = DocumentSummary.objects.filter(
            id__in=document_ids,
            user=request.user
        )
        
        if documents.count() != len(document_ids):
            return Response(
                {'error': 'Some documents not found or not owned by user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count = documents.count()
        documents.delete()
        
        return Response({
            'message': f'Successfully deleted {deleted_count} documents',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        logger.error(f"Bulk delete error: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_update_favorites(request):
    """Bulk update favorite status of documents"""
    try:
        document_ids = request.data.get('document_ids', [])
        is_favorite = request.data.get('is_favorite', True)
        
        if not document_ids:
            return Response(
                {'error': 'No document IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update documents
        updated_count = DocumentSummary.objects.filter(
            id__in=document_ids,
            user=request.user
        ).update(is_favorite=is_favorite)
        
        return Response({
            'message': f'Updated {updated_count} documents',
            'updated_count': updated_count,
            'is_favorite': is_favorite
        })
        
    except Exception as e:
        logger.error(f"Bulk update favorites error: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
