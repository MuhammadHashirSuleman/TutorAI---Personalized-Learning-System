"""
External Platform Integration System
Provides connectors and APIs for integrating with external learning platforms
Supports Moodle, Coursera, and LTI (Learning Tools Interoperability) standards
"""

import requests
import json
import base64
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode, urlparse, parse_qs
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass

from apps.courses.models import Course, Quiz, Subject
from apps.progress.models import StudentProgress, QuizResult
from apps.users.models import StudentProfile

User = get_user_model()
logger = logging.getLogger(__name__)

@dataclass
class ExternalPlatformConfig:
    """Configuration for external platform integration"""
    platform_name: str
    base_url: str
    api_key: str
    secret_key: str
    client_id: str
    client_secret: str
    auth_type: str  # oauth, api_key, basic_auth
    version: str
    enabled: bool

@dataclass
class SyncResult:
    """Result of synchronization operation"""
    success: bool
    items_processed: int
    items_created: int
    items_updated: int
    items_failed: int
    errors: List[str]
    warnings: List[str]
    sync_timestamp: datetime

class ExternalPlatformManager:
    """
    Base class for external platform integrations
    """
    
    def __init__(self, config: ExternalPlatformConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AIStudy-Platform/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def authenticate(self) -> bool:
        """Authenticate with the external platform"""
        raise NotImplementedError("Subclasses must implement authenticate method")
    
    def sync_courses(self) -> SyncResult:
        """Sync courses from external platform"""
        raise NotImplementedError("Subclasses must implement sync_courses method")
    
    def sync_students(self) -> SyncResult:
        """Sync student data from external platform"""
        raise NotImplementedError("Subclasses must implement sync_students method")
    
    def sync_grades(self) -> SyncResult:
        """Sync grades/results to external platform"""
        raise NotImplementedError("Subclasses must implement sync_grades method")
    
    def export_data(self, data_type: str, filters: Dict) -> Dict:
        """Export data to external platform"""
        raise NotImplementedError("Subclasses must implement export_data method")

class MoodleIntegration(ExternalPlatformManager):
    """
    Integration with Moodle Learning Management System
    Uses Moodle Web Services API
    """
    
    def __init__(self, config: ExternalPlatformConfig):
        super().__init__(config)
        self.token = None
        self.user_id = None
    
    def authenticate(self) -> bool:
        """Authenticate with Moodle using web service token"""
        try:
            # Moodle uses token-based authentication
            # In production, token would be configured in settings
            self.token = self.config.api_key
            
            # Test the token by getting site info
            response = self._make_request('core_webservice_get_site_info')
            
            if response and 'sitename' in response:
                logger.info(f"Successfully authenticated with Moodle: {response['sitename']}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Moodle authentication failed: {str(e)}")
            return False
    
    def _make_request(self, function: str, params: Dict = None) -> Optional[Dict]:
        """Make API request to Moodle"""
        try:
            url = f"{self.config.base_url}/webservice/rest/server.php"
            
            data = {
                'wstoken': self.token,
                'wsfunction': function,
                'moodlewsrestformat': 'json'
            }
            
            if params:
                data.update(params)
            
            response = self.session.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            
            if 'exception' in result:
                logger.error(f"Moodle API error: {result['message']}")
                return None
            
            return result
            
        except Exception as e:
            logger.error(f"Moodle API request failed: {str(e)}")
            return None
    
    def sync_courses(self) -> SyncResult:
        """Sync courses from Moodle"""
        result = SyncResult(
            success=True,
            items_processed=0,
            items_created=0,
            items_updated=0,
            items_failed=0,
            errors=[],
            warnings=[],
            sync_timestamp=timezone.now()
        )
        
        try:
            if not self.authenticate():
                result.success = False
                result.errors.append("Authentication failed")
                return result
            
            # Get courses from Moodle
            courses_data = self._make_request('core_course_get_courses')
            
            if not courses_data:
                result.success = False
                result.errors.append("Failed to fetch courses from Moodle")
                return result
            
            with transaction.atomic():
                for course_data in courses_data:
                    result.items_processed += 1
                    
                    try:
                        # Map Moodle course to our Course model
                        course_info = {
                            'title': course_data.get('fullname', course_data.get('shortname')),
                            'description': course_data.get('summary', ''),
                            'external_id': str(course_data.get('id')),
                            'external_platform': 'moodle',
                            'is_active': True
                        }
                        
                        # Check if course already exists
                        existing_course = Course.objects.filter(
                            external_id=course_info['external_id'],
                            external_platform='moodle'
                        ).first()
                        
                        if existing_course:
                            # Update existing course
                            for key, value in course_info.items():
                                setattr(existing_course, key, value)
                            existing_course.save()
                            result.items_updated += 1
                        else:
                            # Create new course
                            # Need to assign an instructor (could be configurable)
                            instructor = User.objects.filter(role='teacher').first()
                            if instructor:
                                course_info['instructor'] = instructor
                                Course.objects.create(**course_info)
                                result.items_created += 1
                            else:
                                result.warnings.append(f"No teacher available for course: {course_info['title']}")
                        
                    except Exception as e:
                        result.items_failed += 1
                        result.errors.append(f"Failed to sync course {course_data.get('id')}: {str(e)}")
            
            logger.info(f"Moodle course sync completed: {result.items_created} created, {result.items_updated} updated")
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Course sync failed: {str(e)}")
            logger.error(f"Moodle course sync error: {str(e)}")
        
        return result
    
    def sync_students(self) -> SyncResult:
        """Sync student enrollments from Moodle"""
        result = SyncResult(
            success=True,
            items_processed=0,
            items_created=0,
            items_updated=0,
            items_failed=0,
            errors=[],
            warnings=[],
            sync_timestamp=timezone.now()
        )
        
        try:
            if not self.authenticate():
                result.success = False
                result.errors.append("Authentication failed")
                return result
            
            # Get enrolled users from Moodle courses
            courses = Course.objects.filter(external_platform='moodle', is_active=True)
            
            for course in courses:
                try:
                    # Get course enrollments from Moodle
                    enrollments_data = self._make_request('core_enrol_get_enrolled_users', {
                        'courseid': int(course.external_id)
                    })
                    
                    if enrollments_data:
                        for user_data in enrollments_data:
                            result.items_processed += 1
                            
                            try:
                                # Create or get student user
                                student, created = User.objects.get_or_create(
                                    email=user_data.get('email', f"moodle_user_{user_data.get('id')}@example.com"),
                                    defaults={
                                        'first_name': user_data.get('firstname', ''),
                                        'last_name': user_data.get('lastname', ''),
                                        'role': 'student',
                                        'is_active': True,
                                        'external_id': str(user_data.get('id')),
                                        'external_platform': 'moodle'
                                    }
                                )
                                
                                if created:
                                    result.items_created += 1
                                    
                                    # Create student profile
                                    StudentProfile.objects.get_or_create(
                                        user=student,
                                        defaults={'learning_preferences': {}}
                                    )
                                
                                # Create course enrollment
                                from apps.courses.models import CourseEnrollment
                                enrollment, enrollment_created = CourseEnrollment.objects.get_or_create(
                                    student=student,
                                    course=course,
                                    defaults={
                                        'enrolled_at': timezone.now(),
                                        'status': 'active'
                                    }
                                )
                                
                                if enrollment_created:
                                    result.items_updated += 1
                                
                            except Exception as e:
                                result.items_failed += 1
                                result.errors.append(f"Failed to sync student {user_data.get('id')}: {str(e)}")
                
                except Exception as e:
                    result.errors.append(f"Failed to sync enrollments for course {course.external_id}: {str(e)}")
            
            logger.info(f"Moodle student sync completed: {result.items_created} created, {result.items_updated} enrollments")
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Student sync failed: {str(e)}")
            logger.error(f"Moodle student sync error: {str(e)}")
        
        return result
    
    def sync_grades(self) -> SyncResult:
        """Sync grades back to Moodle"""
        result = SyncResult(
            success=True,
            items_processed=0,
            items_created=0,
            items_updated=0,
            items_failed=0,
            errors=[],
            warnings=[],
            sync_timestamp=timezone.now()
        )
        
        try:
            if not self.authenticate():
                result.success = False
                result.errors.append("Authentication failed")
                return result
            
            # Get quiz results to sync back to Moodle
            quiz_results = QuizResult.objects.filter(
                quiz__course__external_platform='moodle',
                status='completed',
                synced_to_external=False
            )
            
            for quiz_result in quiz_results:
                result.items_processed += 1
                
                try:
                    # Prepare grade data for Moodle
                    grade_data = {
                        'courseid': int(quiz_result.quiz.course.external_id),
                        'userid': int(quiz_result.student.external_id),
                        'grades': [{
                            'itemname': quiz_result.quiz.title,
                            'rawgrade': quiz_result.score,
                            'feedback': f"AI Study Quiz Score: {quiz_result.score}%"
                        }]
                    }
                    
                    # Send grade to Moodle
                    response = self._make_request('core_grades_update_grades', grade_data)
                    
                    if response:
                        quiz_result.synced_to_external = True
                        quiz_result.external_sync_timestamp = timezone.now()
                        quiz_result.save()
                        result.items_updated += 1
                    else:
                        result.items_failed += 1
                        result.errors.append(f"Failed to sync grade for quiz {quiz_result.id}")
                
                except Exception as e:
                    result.items_failed += 1
                    result.errors.append(f"Failed to sync grade {quiz_result.id}: {str(e)}")
            
            logger.info(f"Moodle grade sync completed: {result.items_updated} grades synced")
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Grade sync failed: {str(e)}")
            logger.error(f"Moodle grade sync error: {str(e)}")
        
        return result
    
    def export_data(self, data_type: str, filters: Dict) -> Dict:
        """Export data to Moodle format"""
        try:
            if data_type == 'courses':
                return self._export_courses(filters)
            elif data_type == 'students':
                return self._export_students(filters)
            elif data_type == 'grades':
                return self._export_grades(filters)
            else:
                return {'error': f'Unsupported data type: {data_type}'}
                
        except Exception as e:
            logger.error(f"Moodle data export error: {str(e)}")
            return {'error': str(e)}
    
    def _export_courses(self, filters: Dict) -> Dict:
        """Export courses in Moodle format"""
        courses = Course.objects.filter(**filters)
        
        exported_data = {
            'courses': [
                {
                    'fullname': course.title,
                    'shortname': course.title[:50],
                    'summary': course.description,
                    'categoryid': 1,  # Default category
                    'visible': 1 if course.is_active else 0,
                    'format': 'weeks'
                }
                for course in courses
            ]
        }
        
        return exported_data
    
    def _export_students(self, filters: Dict) -> Dict:
        """Export students in Moodle format"""
        students = User.objects.filter(role='student', **filters)
        
        exported_data = {
            'users': [
                {
                    'username': student.email,
                    'firstname': student.first_name,
                    'lastname': student.last_name,
                    'email': student.email,
                    'auth': 'manual',
                    'password': 'changeme123',  # Default password
                    'lang': 'en'
                }
                for student in students
            ]
        }
        
        return exported_data
    
    def _export_grades(self, filters: Dict) -> Dict:
        """Export grades in Moodle format"""
        quiz_results = QuizResult.objects.filter(**filters)
        
        exported_data = {
            'grades': [
                {
                    'userid': result.student.external_id or result.student.email,
                    'courseid': result.quiz.course.external_id,
                    'itemname': result.quiz.title,
                    'rawgrade': result.score,
                    'feedback': f"AI Study Score: {result.score}%"
                }
                for result in quiz_results
            ]
        }
        
        return exported_data

class CourseraIntegration(ExternalPlatformManager):
    """
    Integration with Coursera platform
    Uses Coursera Partner API
    """
    
    def __init__(self, config: ExternalPlatformConfig):
        super().__init__(config)
        self.access_token = None
    
    def authenticate(self) -> bool:
        """Authenticate with Coursera using OAuth2"""
        try:
            # OAuth2 authentication flow for Coursera
            auth_url = f"{self.config.base_url}/oauth2/client_credentials/token"
            
            auth_data = {
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret,
                'grant_type': 'client_credentials'
            }
            
            response = self.session.post(auth_url, data=auth_data)
            response.raise_for_status()
            
            auth_result = response.json()
            self.access_token = auth_result.get('access_token')
            
            if self.access_token:
                self.session.headers['Authorization'] = f'Bearer {self.access_token}'
                logger.info("Successfully authenticated with Coursera")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Coursera authentication failed: {str(e)}")
            return False
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Optional[Dict]:
        """Make API request to Coursera"""
        try:
            url = f"{self.config.base_url}/{endpoint}"
            
            if method.upper() == 'GET':
                response = self.session.get(url, params=data)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Coursera API request failed: {str(e)}")
            return None
    
    def sync_courses(self) -> SyncResult:
        """Sync courses from Coursera"""
        result = SyncResult(
            success=True,
            items_processed=0,
            items_created=0,
            items_updated=0,
            items_failed=0,
            errors=[],
            warnings=[],
            sync_timestamp=timezone.now()
        )
        
        try:
            if not self.authenticate():
                result.success = False
                result.errors.append("Authentication failed")
                return result
            
            # Get courses from Coursera
            courses_data = self._make_request('courses')
            
            if not courses_data or 'elements' not in courses_data:
                result.success = False
                result.errors.append("Failed to fetch courses from Coursera")
                return result
            
            with transaction.atomic():
                for course_data in courses_data['elements']:
                    result.items_processed += 1
                    
                    try:
                        course_info = {
                            'title': course_data.get('name', 'Untitled Course'),
                            'description': course_data.get('description', ''),
                            'external_id': course_data.get('slug'),
                            'external_platform': 'coursera',
                            'is_active': course_data.get('courseStatus') == 'launched'
                        }
                        
                        existing_course = Course.objects.filter(
                            external_id=course_info['external_id'],
                            external_platform='coursera'
                        ).first()
                        
                        if existing_course:
                            for key, value in course_info.items():
                                setattr(existing_course, key, value)
                            existing_course.save()
                            result.items_updated += 1
                        else:
                            instructor = User.objects.filter(role='teacher').first()
                            if instructor:
                                course_info['instructor'] = instructor
                                Course.objects.create(**course_info)
                                result.items_created += 1
                            else:
                                result.warnings.append(f"No teacher available for course: {course_info['title']}")
                    
                    except Exception as e:
                        result.items_failed += 1
                        result.errors.append(f"Failed to sync course {course_data.get('slug')}: {str(e)}")
            
            logger.info(f"Coursera course sync completed: {result.items_created} created, {result.items_updated} updated")
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Course sync failed: {str(e)}")
            logger.error(f"Coursera course sync error: {str(e)}")
        
        return result
    
    def sync_students(self) -> SyncResult:
        """Sync student data from Coursera (limited by API access)"""
        result = SyncResult(
            success=True,
            items_processed=0,
            items_created=0,
            items_updated=0,
            items_failed=0,
            errors=[],
            warnings=[],
            sync_timestamp=timezone.now()
        )
        
        # Note: Coursera Partner API has limited access to learner data
        # This would typically require special permissions and agreements
        result.warnings.append("Coursera student data sync requires special API access permissions")
        
        return result
    
    def sync_grades(self) -> SyncResult:
        """Sync grades to Coursera (if supported)"""
        result = SyncResult(
            success=True,
            items_processed=0,
            items_created=0,
            items_updated=0,
            items_failed=0,
            errors=[],
            warnings=[],
            sync_timestamp=timezone.now()
        )
        
        result.warnings.append("Grade sync to Coursera requires special integration agreements")
        
        return result
    
    def export_data(self, data_type: str, filters: Dict) -> Dict:
        """Export data in Coursera format"""
        try:
            if data_type == 'courses':
                return self._export_courses_coursera(filters)
            else:
                return {'error': f'Unsupported data type for Coursera: {data_type}'}
                
        except Exception as e:
            logger.error(f"Coursera data export error: {str(e)}")
            return {'error': str(e)}
    
    def _export_courses_coursera(self, filters: Dict) -> Dict:
        """Export courses in Coursera format"""
        courses = Course.objects.filter(**filters)
        
        exported_data = {
            'courses': [
                {
                    'name': course.title,
                    'description': course.description,
                    'slug': course.title.lower().replace(' ', '-')[:50],
                    'courseStatus': 'launched' if course.is_active else 'draft',
                    'workload': '3-5 hours per week',
                    'language': 'en'
                }
                for course in courses
            ]
        }
        
        return exported_data

class LTIIntegration(ExternalPlatformManager):
    """
    Learning Tools Interoperability (LTI) Standard Integration
    Supports LTI 1.1 and basic LTI 1.3 features
    """
    
    def __init__(self, config: ExternalPlatformConfig):
        super().__init__(config)
        self.consumer_key = config.client_id
        self.shared_secret = config.client_secret
    
    def authenticate(self) -> bool:
        """LTI uses request-level authentication"""
        # LTI doesn't use session-based authentication
        # Authentication happens per request using OAuth signatures
        return True
    
    def get_connection_info(self) -> Dict:
        """Get LTI connection information"""
        return {
            'platform': 'lti',
            'status': 'ready',
            'consumer_key_configured': bool(self.consumer_key),
            'shared_secret_configured': bool(self.shared_secret),
            'version_supported': 'LTI 1.1/1.2',
            'authentication_type': 'OAuth 1.0 signature'
        }
    
    def validate_lti_request(self, request_data: Dict) -> bool:
        """Validate incoming LTI request"""
        try:
            # Extract OAuth parameters
            oauth_signature = request_data.get('oauth_signature')
            oauth_consumer_key = request_data.get('oauth_consumer_key')
            
            if oauth_consumer_key != self.consumer_key:
                return False
            
            # Generate signature for validation
            expected_signature = self._generate_oauth_signature(request_data)
            
            return oauth_signature == expected_signature
            
        except Exception as e:
            logger.error(f"LTI request validation error: {str(e)}")
            return False
    
    def _generate_oauth_signature(self, request_data: Dict) -> str:
        """Generate OAuth 1.0 signature for LTI"""
        try:
            # Normalize parameters
            normalized_params = self._normalize_parameters(request_data)
            
            # Create signature base string
            signature_base = f"POST&{self._url_encode(request_data.get('launch_url', ''))}&{self._url_encode(normalized_params)}"
            
            # Create signing key
            signing_key = f"{self._url_encode(self.shared_secret)}&"
            
            # Generate HMAC-SHA1 signature
            signature = hmac.new(
                signing_key.encode('utf-8'),
                signature_base.encode('utf-8'),
                hashlib.sha1
            ).digest()
            
            return base64.b64encode(signature).decode('utf-8')
            
        except Exception as e:
            logger.error(f"OAuth signature generation error: {str(e)}")
            return ""
    
    def _normalize_parameters(self, params: Dict) -> str:
        """Normalize OAuth parameters"""
        normalized = []
        
        for key, value in sorted(params.items()):
            if key != 'oauth_signature':
                normalized.append(f"{self._url_encode(str(key))}={self._url_encode(str(value))}")
        
        return "&".join(normalized)
    
    def _url_encode(self, value: str) -> str:
        """URL encode value according to OAuth spec"""
        return requests.utils.quote(str(value), safe='')
    
    def process_lti_launch(self, request_data: Dict) -> Dict:
        """Process LTI launch request"""
        try:
            if not self.validate_lti_request(request_data):
                return {'error': 'Invalid LTI request signature'}
            
            # Extract user information
            user_info = {
                'user_id': request_data.get('user_id'),
                'lis_person_name_given': request_data.get('lis_person_name_given', ''),
                'lis_person_name_family': request_data.get('lis_person_name_family', ''),
                'lis_person_contact_email_primary': request_data.get('lis_person_contact_email_primary', ''),
                'roles': request_data.get('roles', ''),
            }
            
            # Extract context information
            context_info = {
                'context_id': request_data.get('context_id'),
                'context_title': request_data.get('context_title', ''),
                'context_label': request_data.get('context_label', ''),
            }
            
            # Extract resource information
            resource_info = {
                'resource_link_id': request_data.get('resource_link_id'),
                'resource_link_title': request_data.get('resource_link_title', ''),
                'resource_link_description': request_data.get('resource_link_description', ''),
            }
            
            # Create or update user
            user = self._create_or_update_lti_user(user_info)
            
            # Create or update course
            course = self._create_or_update_lti_course(context_info, user)
            
            # Create launch session
            launch_session = {
                'user': user,
                'course': course,
                'resource_link_id': resource_info['resource_link_id'],
                'launch_timestamp': timezone.now(),
                'return_url': request_data.get('launch_presentation_return_url'),
            }
            
            return {
                'success': True,
                'launch_session': launch_session,
                'redirect_url': f'/lti/course/{course.id}/'
            }
            
        except Exception as e:
            logger.error(f"LTI launch processing error: {str(e)}")
            return {'error': str(e)}
    
    def _create_or_update_lti_user(self, user_info: Dict) -> User:
        """Create or update user from LTI data"""
        email = user_info.get('lis_person_contact_email_primary')
        external_id = user_info.get('user_id')
        
        if not email and not external_id:
            raise ValueError("No user identifier provided in LTI request")
        
        # Determine user role
        roles = user_info.get('roles', '').lower()
        if 'instructor' in roles or 'teacher' in roles:
            user_role = 'teacher'
        else:
            user_role = 'student'
        
        # Create or get user
        user, created = User.objects.get_or_create(
            email=email or f"lti_user_{external_id}@example.com",
            defaults={
                'first_name': user_info.get('lis_person_name_given', ''),
                'last_name': user_info.get('lis_person_name_family', ''),
                'role': user_role,
                'is_active': True,
                'external_id': external_id,
                'external_platform': 'lti'
            }
        )
        
        if not created:
            # Update existing user
            user.first_name = user_info.get('lis_person_name_given', user.first_name)
            user.last_name = user_info.get('lis_person_name_family', user.last_name)
            user.save()
        
        return user
    
    def _create_or_update_lti_course(self, context_info: Dict, instructor: User) -> Course:
        """Create or update course from LTI context"""
        context_id = context_info.get('context_id')
        
        if not context_id:
            raise ValueError("No context ID provided in LTI request")
        
        course, created = Course.objects.get_or_create(
            external_id=context_id,
            external_platform='lti',
            defaults={
                'title': context_info.get('context_title', 'LTI Course'),
                'description': f"Course from LTI context: {context_info.get('context_label', '')}",
                'instructor': instructor if instructor.role == 'teacher' else User.objects.filter(role='teacher').first(),
                'is_active': True
            }
        )
        
        if not created:
            # Update existing course
            course.title = context_info.get('context_title', course.title)
            course.save()
        
        return course
    
    def send_grade_back(self, launch_session: Dict, grade: float) -> bool:
        """Send grade back to LTI consumer"""
        try:
            return_url = launch_session.get('return_url')
            if not return_url:
                logger.warning("No return URL available for grade passback")
                return False
            
            # Construct grade passback (simplified - real implementation would use proper LTI grade passback)
            grade_data = {
                'lis_result_sourcedid': launch_session.get('resource_link_id'),
                'lis_outcome_service_url': return_url,
                'grade': grade / 100.0,  # Convert percentage to decimal
            }
            
            # In a real implementation, this would use proper LTI outcomes service
            logger.info(f"Grade passback simulated: {grade_data}")
            
            return True
            
        except Exception as e:
            logger.error(f"LTI grade passback error: {str(e)}")
            return False
    
    def sync_courses(self) -> SyncResult:
        """LTI courses are created on-demand during launch"""
        return SyncResult(
            success=True,
            items_processed=0,
            items_created=0,
            items_updated=0,
            items_failed=0,
            errors=[],
            warnings=["LTI courses are created automatically during launch"],
            sync_timestamp=timezone.now()
        )
    
    def sync_students(self) -> SyncResult:
        """LTI students are created on-demand during launch"""
        return SyncResult(
            success=True,
            items_processed=0,
            items_created=0,
            items_updated=0,
            items_failed=0,
            errors=[],
            warnings=["LTI students are created automatically during launch"],
            sync_timestamp=timezone.now()
        )
    
    def sync_grades(self) -> SyncResult:
        """Sync grades back via LTI outcomes service"""
        result = SyncResult(
            success=True,
            items_processed=0,
            items_created=0,
            items_updated=0,
            items_failed=0,
            errors=[],
            warnings=[],
            sync_timestamp=timezone.now()
        )
        
        # In a real implementation, this would sync grades back to LTI consumers
        result.warnings.append("LTI grade sync requires active launch sessions")
        
        return result
    
    def export_data(self, data_type: str, filters: Dict) -> Dict:
        """Export data in LTI format"""
        return {'warning': 'LTI is primarily a consumer protocol, not for bulk data export'}

# Platform factory
class ExternalPlatformFactory:
    """Factory for creating external platform integrations"""
    
    @staticmethod
    def create_integration(platform_name: str) -> Optional[ExternalPlatformManager]:
        """Create integration instance for specified platform"""
        try:
            config = ExternalPlatformFactory._get_platform_config(platform_name)
            
            if not config.enabled:
                logger.warning(f"Platform {platform_name} is not enabled")
                return None
            
            if platform_name.lower() == 'moodle':
                return MoodleIntegration(config)
            elif platform_name.lower() == 'coursera':
                return CourseraIntegration(config)
            elif platform_name.lower() == 'lti':
                return LTIIntegration(config)
            else:
                logger.error(f"Unsupported platform: {platform_name}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create integration for {platform_name}: {str(e)}")
            return None
    
    @staticmethod
    def _get_platform_config(platform_name: str) -> ExternalPlatformConfig:
        """Get configuration for platform"""
        platform_configs = {
            'moodle': ExternalPlatformConfig(
                platform_name='moodle',
                base_url=getattr(settings, 'MOODLE_BASE_URL', 'https://your-moodle-site.com'),
                api_key=getattr(settings, 'MOODLE_API_KEY', ''),
                secret_key=getattr(settings, 'MOODLE_SECRET_KEY', ''),
                client_id='',
                client_secret='',
                auth_type='api_key',
                version='3.11',
                enabled=getattr(settings, 'MOODLE_INTEGRATION_ENABLED', False)
            ),
            'coursera': ExternalPlatformConfig(
                platform_name='coursera',
                base_url=getattr(settings, 'COURSERA_BASE_URL', 'https://api.coursera.org/api/rest/v1'),
                api_key=getattr(settings, 'COURSERA_API_KEY', ''),
                secret_key=getattr(settings, 'COURSERA_SECRET_KEY', ''),
                client_id=getattr(settings, 'COURSERA_CLIENT_ID', ''),
                client_secret=getattr(settings, 'COURSERA_CLIENT_SECRET', ''),
                auth_type='oauth',
                version='1.0',
                enabled=getattr(settings, 'COURSERA_INTEGRATION_ENABLED', False)
            ),
            'lti': ExternalPlatformConfig(
                platform_name='lti',
                base_url='',  # LTI doesn't have a fixed base URL
                api_key='',
                secret_key=getattr(settings, 'LTI_SHARED_SECRET', 'default_secret'),
                client_id=getattr(settings, 'LTI_CONSUMER_KEY', 'ai_study_lti'),
                client_secret=getattr(settings, 'LTI_SHARED_SECRET', 'default_secret'),
                auth_type='oauth',
                version='1.1',
                enabled=getattr(settings, 'LTI_INTEGRATION_ENABLED', True)
            )
        }
        
        return platform_configs.get(platform_name.lower(), ExternalPlatformConfig(
            platform_name=platform_name,
            base_url='',
            api_key='',
            secret_key='',
            client_id='',
            client_secret='',
            auth_type='',
            version='',
            enabled=False
        ))

# Singleton instances
def get_moodle_integration():
    return ExternalPlatformFactory.create_integration('moodle')

def get_coursera_integration():
    return ExternalPlatformFactory.create_integration('coursera')

def get_lti_integration():
    return ExternalPlatformFactory.create_integration('lti')
