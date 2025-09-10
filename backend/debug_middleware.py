import logging

logger = logging.getLogger(__name__)

class DocumentUploadDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log all document upload requests
        if 'documents/upload' in request.path:
            logger.error(f"🔍 DOCUMENT UPLOAD DEBUG:")
            logger.error(f"   Path: {request.path}")
            logger.error(f"   Method: {request.method}")
            logger.error(f"   Content-Type: {request.content_type}")
            logger.error(f"   User authenticated: {request.user.is_authenticated if hasattr(request, 'user') else 'Unknown'}")
            logger.error(f"   POST data keys: {list(request.POST.keys()) if hasattr(request, 'POST') else 'No POST'}")
            logger.error(f"   FILES keys: {list(request.FILES.keys()) if hasattr(request, 'FILES') else 'No FILES'}")
            logger.error(f"   Headers: {dict(request.headers)}")
            
        response = self.get_response(request)
        
        # Log response for document upload
        if 'documents/upload' in request.path:
            logger.error(f"   Response status: {response.status_code}")
            if hasattr(response, 'content'):
                try:
                    content = response.content.decode('utf-8')[:500]  # First 500 chars
                    logger.error(f"   Response content: {content}")
                except:
                    logger.error(f"   Response content: [Could not decode]")
        
        return response
