from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class AuthToken(models.Model):
    """Custom authentication token model"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    token_type = models.CharField(max_length=20, choices=[
        ('access', 'Access Token'),
        ('refresh', 'Refresh Token'),
        ('email_verification', 'Email Verification'),
        ('password_reset', 'Password Reset')
    ])
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'auth_tokens'
        ordering = ['-created_at']
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"{self.user.email} - {self.token_type}"

class LoginHistory(models.Model):
    """Track user login history"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    is_successful = models.BooleanField(default=True)
    location = models.CharField(max_length=100, blank=True)
    device_info = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'login_history'
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.email} - {self.login_time}"
