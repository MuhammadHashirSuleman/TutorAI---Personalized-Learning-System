from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from apps.users.models import StudentProfile

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer - matches frontend form exactly"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role'
        ]
    
    def validate(self, attrs):
        print(f'🔍 Validating registration data: {list(attrs.keys())}')
        
        # Check required fields
        required_fields = ['password', 'password_confirm', 'email', 'username']
        missing_fields = [field for field in required_fields if field not in attrs or not attrs[field]]
        if missing_fields:
            print(f'❌ Missing required fields: {missing_fields}')
            raise serializers.ValidationError(f"Missing required fields: {missing_fields}")
            
        if attrs['password'] != attrs['password_confirm']:
            print('❌ Password mismatch')
            raise serializers.ValidationError("Password and password confirmation do not match.")
        
        print('✅ Registration validation passed')
        return attrs
    
    def create(self, validated_data):
        print('\n🔍 Starting user registration...')
        print('📝 Validated data:', validated_data)
        
        validated_data.pop('password_confirm')
        print('🔐 Creating user with data:', {k: v for k, v in validated_data.items() if k != 'password'})
        
        try:
            user = User.objects.create_user(**validated_data)
            print(f'✅ User created: {user.id} - {user.email} ({user.role})')
            
            # Create student profile (only students and admins in AI system)
            if user.role == User.UserRole.STUDENT:
                print('👨‍🎓 Creating student profile...')
                StudentProfile.objects.create(user=user)
                print('✅ Student profile created successfully')
            # Admins don't need a profile, just user account
            
            return user
        except Exception as e:
            print(f'❌ Error in user creation: {e}')
            import traceback
            traceback.print_exc()
            raise

class LoginSerializer(serializers.Serializer):
    """User login serializer"""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is deactivated.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password.')

class PasswordChangeSerializer(serializers.Serializer):
    """Password change serializer"""
    
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New password and confirmation do not match.")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value

class PasswordResetSerializer(serializers.Serializer):
    """Password reset request serializer"""
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('No user found with this email address.')
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    """Password reset confirmation serializer"""
    
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Password and confirmation do not match.")
        return attrs
