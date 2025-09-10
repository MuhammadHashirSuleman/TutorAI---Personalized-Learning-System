from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import StudentProfile, Note
from apps.courses.models import Subject

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Base user serializer - matches current User model"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone_number', 'date_of_birth', 'profile_picture',
            'is_verified', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'is_verified']

class StudentProfileSerializer(serializers.ModelSerializer):
    """Student profile serializer - matches current model"""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user', 'learning_style', 'learning_goals', 
            'strengths', 'weaknesses', 'preferences'
        ]

class SubjectSerializer(serializers.ModelSerializer):
    """Simple subject serializer"""
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'description']



class UserProfileSerializer(serializers.ModelSerializer):
    """Complete user profile serializer with student data only"""
    
    student_profile = StudentProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone_number', 'date_of_birth', 'profile_picture',
            'is_verified', 'created_at', 'student_profile'
        ]
        read_only_fields = ['id', 'created_at', 'is_verified']

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'date_of_birth'
        ]

class NoteSerializer(serializers.ModelSerializer):
    """Note serializer"""
    
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'content', 'subject', 'tags',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
