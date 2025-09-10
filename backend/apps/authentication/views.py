from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .serializers import (
    UserRegistrationSerializer, LoginSerializer, 
    PasswordChangeSerializer, PasswordResetSerializer,
    PasswordResetConfirmSerializer
)
from .models import LoginHistory, AuthToken
from apps.users.serializers import UserProfileSerializer

User = get_user_model()

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint"""
    print(f'\n📥 Registration request received:')
    print(f'📋 Request data: {request.data}')
    print(f'📋 Content type: {request.content_type}')
    print(f'📋 Request method: {request.method}')
    
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        print('✅ Serializer validation passed')
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    print('❌ Serializer validation failed:')
    print(f'🔍 Errors: {serializer.errors}')
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User login endpoint"""
    print(f'\n📥 Login request received:')
    print(f'📋 Request data: {request.data}')
    print(f'📋 Content type: {request.content_type}')
    print(f'📋 Request method: {request.method}')
    
    serializer = LoginSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        # Record login history
        LoginHistory.objects.create(
            user=user,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            is_successful=True,
            device_info={
                'platform': request.META.get('HTTP_SEC_CH_UA_PLATFORM', ''),
                'mobile': request.META.get('HTTP_SEC_CH_UA_MOBILE', ''),
            }
        )
        
        return Response({
            'message': 'Login successful',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)
    
    print('❌ Login serializer validation failed:')
    print(f'🔍 Errors: {serializer.errors}')
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """User logout endpoint"""
    print(f'\n📥 Logout request received:')
    print(f'📋 Request data: {request.data}')
    print(f'📋 User: {request.user}')
    
    try:
        if "refresh_token" not in request.data:
            print('❌ Missing refresh_token in request data')
            return Response({
                'error': 'refresh_token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        refresh_token = request.data["refresh_token"]
        print(f'🔑 Refresh token: {refresh_token[:50]}...')
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            print('✅ Token blacklisted successfully')
        except Exception as token_error:
            print(f'⚠️ Token blacklist warning: {token_error}')
            # Continue with logout even if blacklisting fails
        
        # Update logout time in login history
        login_record = LoginHistory.objects.filter(
            user=request.user,
            logout_time__isnull=True
        ).first()
        
        if login_record:
            login_record.logout_time = timezone.now()
            login_record.save()
        
        return Response({
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password"""
    serializer = PasswordChangeSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Get user profile"""
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def login_history(request):
    """Get user login history"""
    history = LoginHistory.objects.filter(user=request.user)[:10]
    
    history_data = []
    for record in history:
        history_data.append({
            'ip_address': record.ip_address,
            'login_time': record.login_time,
            'logout_time': record.logout_time,
            'location': record.location,
            'is_successful': record.is_successful,
            'device_info': record.device_info
        })
    
    return Response({
        'login_history': history_data
    })

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
