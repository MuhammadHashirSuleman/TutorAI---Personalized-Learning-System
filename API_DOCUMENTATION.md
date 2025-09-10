# 📚 AIStudy API Documentation

This document provides comprehensive information about the AIStudy platform's REST API endpoints, authentication, request/response formats, and usage examples.

## 🔑 Authentication

AIStudy uses JWT (JSON Web Tokens) for authentication. All protected endpoints require a valid JWT token in the Authorization header.

### Authentication Flow

1. **Register/Login**: Obtain JWT tokens
2. **Include Token**: Add token to Authorization header
3. **Refresh Token**: Use refresh token when access token expires

### Token Format

```
Authorization: Bearer <your_jwt_token>
```

## 🏗️ Base URL

```
Development: http://localhost:8000/api/
Production: https://your-domain.com/api/
```

## 📋 API Endpoints

### Authentication Endpoints

#### POST /auth/register/
Register a new user account.

**Request Body:**
```json
{
    "username": "student123",
    "email": "student@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student"
}
```

**Response (201 Created):**
```json
{
    "user": {
        "id": 1,
        "username": "student123",
        "email": "student@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "student"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

#### POST /auth/login/
Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
    "email": "student@example.com",
    "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
    "user": {
        "id": 1,
        "username": "student123",
        "email": "student@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "student"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

#### POST /auth/logout/
Logout user (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "message": "Successfully logged out"
}
```

#### GET /auth/profile/
Get current user profile (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "student123",
    "email": "student@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "date_joined": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-15T14:20:00Z"
}
```

### Course Management

#### GET /courses/
List all available courses.

**Query Parameters:**
- `page` (optional): Page number for pagination
- `limit` (optional): Number of courses per page
- `category` (optional): Filter by course category
- `search` (optional): Search courses by title or description

**Response (200 OK):**
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/courses/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Introduction to Python Programming",
            "description": "Learn Python from basics to advanced concepts",
            "category": "Programming",
            "difficulty_level": "Beginner",
            "external_url": "https://example.com/course/python",
            "platform": "Udemy",
            "rating": 4.5,
            "duration": "40 hours",
            "created_at": "2024-01-10T12:00:00Z"
        }
    ]
}
```

#### GET /courses/{id}/
Get detailed information about a specific course.

**Response (200 OK):**
```json
{
    "id": 1,
    "title": "Introduction to Python Programming",
    "description": "Learn Python from basics to advanced concepts",
    "category": "Programming",
    "difficulty_level": "Beginner",
    "external_url": "https://example.com/course/python",
    "platform": "Udemy",
    "rating": 4.5,
    "duration": "40 hours",
    "prerequisites": ["Basic computer knowledge"],
    "learning_objectives": [
        "Understand Python syntax",
        "Build simple applications",
        "Work with data structures"
    ],
    "created_at": "2024-01-10T12:00:00Z"
}
```

### AI Services

#### POST /chatbot/chat/
Interact with the AI tutor chatbot.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "message": "Can you explain what machine learning is?",
    "context": {
        "subject": "Computer Science",
        "current_topic": "Artificial Intelligence"
    }
}
```

**Response (200 OK):**
```json
{
    "response": "Machine learning is a subset of artificial intelligence (AI) that enables computers to learn and improve from experience without being explicitly programmed...",
    "conversation_id": "conv_123456789",
    "timestamp": "2024-01-15T14:30:00Z",
    "tokens_used": 150
}
```

#### POST /summarizer/document/
Summarize uploaded documents using AI.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
- `file`: Document file (PDF, DOCX, TXT)
- `summary_length`: "short" | "medium" | "long"
- `focus_areas`: JSON array of topics to focus on

**Response (200 OK):**
```json
{
    "summary": "This document covers the fundamentals of machine learning, including supervised and unsupervised learning techniques...",
    "key_points": [
        "Machine learning algorithms can be categorized into supervised and unsupervised",
        "Training data quality significantly impacts model performance",
        "Cross-validation helps prevent overfitting"
    ],
    "word_count": {
        "original": 5000,
        "summary": 250
    },
    "processing_time": 3.2
}
```

#### GET /recommendations/
Get personalized learning recommendations.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `limit` (optional): Number of recommendations
- `category` (optional): Filter by category

**Response (200 OK):**
```json
{
    "recommendations": [
        {
            "type": "course",
            "item_id": 15,
            "title": "Advanced Machine Learning",
            "reason": "Based on your progress in Introduction to ML",
            "confidence_score": 0.85,
            "estimated_time": "60 hours"
        },
        {
            "type": "practice",
            "item_id": 8,
            "title": "Python Data Structures Quiz",
            "reason": "Reinforce your Python fundamentals",
            "confidence_score": 0.78,
            "estimated_time": "30 minutes"
        }
    ],
    "total_count": 12,
    "last_updated": "2024-01-15T12:00:00Z"
}
```

### Progress Tracking

#### GET /progress/
Get user's learning progress.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "overall_progress": {
        "courses_enrolled": 5,
        "courses_completed": 2,
        "total_study_time": 120.5,
        "current_streak": 7,
        "level": "Intermediate"
    },
    "recent_activity": [
        {
            "type": "course_progress",
            "course_id": 3,
            "course_title": "Data Science Fundamentals",
            "progress_percentage": 75,
            "last_accessed": "2024-01-15T13:45:00Z"
        }
    ],
    "achievements": [
        {
            "id": 1,
            "title": "First Course Completed",
            "description": "Completed your first course",
            "earned_date": "2024-01-10T18:30:00Z"
        }
    ]
}
```

#### POST /progress/update/
Update progress for a specific lesson or course.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "course_id": 3,
    "lesson_id": 12,
    "progress_percentage": 100,
    "time_spent": 45,
    "completed": true
}
```

**Response (200 OK):**
```json
{
    "message": "Progress updated successfully",
    "course_progress": {
        "course_id": 3,
        "overall_percentage": 78,
        "lessons_completed": 12,
        "total_lessons": 15
    }
}
```


### User Management

#### GET /users/profile/
Get detailed user profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "student123",
    "email": "student@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "profile": {
        "bio": "Passionate about machine learning",
        "learning_goals": ["Master Python", "Understand AI"],
        "preferred_learning_style": "Visual",
        "timezone": "America/New_York"
    },
    "statistics": {
        "courses_completed": 5,
        "total_study_hours": 120,
        "assessments_taken": 15,
        "current_streak": 7
    }
}
```

#### PUT /users/profile/
Update user profile information.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "first_name": "John",
    "last_name": "Smith",
    "profile": {
        "bio": "Updated bio",
        "learning_goals": ["Master Python", "Learn Data Science"],
        "preferred_learning_style": "Hands-on"
    }
}
```

**Response (200 OK):**
```json
{
    "message": "Profile updated successfully",
    "user": {
        "id": 1,
        "first_name": "John",
        "last_name": "Smith",
        "profile": {
            "bio": "Updated bio",
            "learning_goals": ["Master Python", "Learn Data Science"],
            "preferred_learning_style": "Hands-on"
        }
    }
}
```

## 🔄 Error Handling

The API uses standard HTTP status codes and returns detailed error information.

### Error Response Format

```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "The provided data is invalid",
        "details": {
            "email": ["This field is required"],
            "password": ["Password must be at least 8 characters"]
        }
    },
    "timestamp": "2024-01-15T14:30:00Z"
}
```

### Common Error Codes

- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## 📊 Rate Limiting

API endpoints are rate-limited to ensure fair usage:

- **Authentication endpoints**: 5 requests per minute
- **AI Services**: 10 requests per minute
- **General endpoints**: 60 requests per minute

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642262400
```

## 🔧 SDK and Code Examples

### Python Example

```python
import requests

# Authentication
def login(email, password):
    response = requests.post('http://localhost:8000/api/auth/login/', {
        'email': email,
        'password': password
    })
    return response.json()

# Get courses with authentication
def get_courses(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get('http://localhost:8000/api/courses/', headers=headers)
    return response.json()

# Chat with AI tutor
def chat_with_ai(token, message):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {'message': message}
    response = requests.post('http://localhost:8000/api/chatbot/chat/', 
                           json=data, headers=headers)
    return response.json()
```

### JavaScript Example

```javascript
// Authentication
async function login(email, password) {
    const response = await fetch('http://localhost:8000/api/auth/login/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, password})
    });
    return response.json();
}

// Get user progress
async function getUserProgress(token) {
    const response = await fetch('http://localhost:8000/api/progress/', {
        headers: {'Authorization': `Bearer ${token}`}
    });
    return response.json();
}

// Submit assessment
async function submitAssessment(token, assessmentId, answers) {
    const response = await fetch('http://localhost:8000/api/assessments/submit/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            assessment_id: assessmentId,
            answers: answers
        })
    });
    return response.json();
}
```

## 📋 Testing

### Testing with cURL

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "student@example.com", "password": "password123"}'

# Get courses (with authentication)
curl -X GET http://localhost:8000/api/courses/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Chat with AI
curl -X POST http://localhost:8000/api/chatbot/chat/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain machine learning"}'
```

## 📈 API Versioning

The API uses URL versioning:

- Current version: `v1`
- Base URL: `/api/v1/`

When breaking changes are introduced, a new version will be created while maintaining backward compatibility for existing versions.

---

For more information, visit the interactive API documentation at `http://localhost:8000/api/docs/` when running the development server.
