"""
Security middleware for the AI Learning System
"""
from django.utils.deprecation import MiddlewareMixin


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to responses
    """
    
    def process_response(self, request, response):
        """
        Add security headers to response
        """
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Prevent content type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Only allow HTTPS connections (if not in debug mode)
        if not getattr(request, 'DEBUG', False):
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Prevent referrer information leakage
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy
        response['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:;"
        
        return response
