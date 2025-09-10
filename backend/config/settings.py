import os
from pathlib import Path
from decouple import config
from datetime import timedelta

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,testserver', cast=lambda v: [s.strip() for s in v.split(',')])

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.users',
    'apps.authentication', 
    'apps.courses',
    'apps.assessments',
    'apps.progress',
    'apps.chatbot',
    'apps.recommendations',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'debug_middleware.DocumentUploadDebugMiddleware',  # Debug middleware first
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='ai_learning_system'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'sql_mode': 'traditional',
        }
    }
}

# Cache configuration (using database cache instead of Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_table',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),  # Extended to 24 hours for development
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),  # Extended to 30 days
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
}

# CORS settings - Completely permissive for debugging
CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = []

CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOWED_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# AI Configuration
OPENROUTER_API_KEY = config('OPENROUTER_API_KEY', default='')
OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1'

# DeepSeek API Configuration
DEEPSEEK_API_KEY = config('DEEPSEEK_API_KEY', default='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')

# External Platform Integrations
# Moodle Integration
MOODLE_INTEGRATION_ENABLED = config('MOODLE_INTEGRATION_ENABLED', default=False, cast=bool)
MOODLE_BASE_URL = config('MOODLE_BASE_URL', default='https://your-moodle-site.com')
MOODLE_API_KEY = config('MOODLE_API_KEY', default='')
MOODLE_SECRET_KEY = config('MOODLE_SECRET_KEY', default='')

# Coursera Integration
COURSERA_INTEGRATION_ENABLED = config('COURSERA_INTEGRATION_ENABLED', default=False, cast=bool)
COURSERA_BASE_URL = config('COURSERA_BASE_URL', default='https://api.coursera.org/api/rest/v1')
COURSERA_CLIENT_ID = config('COURSERA_CLIENT_ID', default='')
COURSERA_CLIENT_SECRET = config('COURSERA_CLIENT_SECRET', default='')
COURSERA_API_KEY = config('COURSERA_API_KEY', default='')
COURSERA_SECRET_KEY = config('COURSERA_SECRET_KEY', default='')

# LTI (Learning Tools Interoperability) Integration
LTI_INTEGRATION_ENABLED = config('LTI_INTEGRATION_ENABLED', default=True, cast=bool)
LTI_CONSUMER_KEY = config('LTI_CONSUMER_KEY', default='ai_study_lti')
LTI_SHARED_SECRET = config('LTI_SHARED_SECRET', default='ai_study_secret_2024')

# AI Model Settings
AI_MODELS = {
    'DEEPSEEK': 'deepseek/deepseek-chat',
    'LLAMA': 'meta-llama/llama-3.1-70b-instruct',
}

# Celery Configuration (using database instead of Redis)
CELERY_BROKER_URL = 'django://'
CELERY_RESULT_BACKEND = 'django://'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'AI Learning System API',
    'DESCRIPTION': 'API for AI-Powered Personalized Learning System',
    'VERSION': '1.0.0',
}
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
