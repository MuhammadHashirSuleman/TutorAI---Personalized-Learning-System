# 🤝 Contributing to AIStudy

Thank you for your interest in contributing to AIStudy! This guide will help you get started with contributing to our AI-powered learning platform.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)
- [Development Workflow](#development-workflow)

## 📖 Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. By participating, you are expected to uphold this code.

### Our Pledge

We are committed to making participation in this project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** with pip
- **Node.js 16+** with npm
- **MySQL 8.0+** or another supported database
- **Git**
- Code editor (VS Code, PyCharm, etc.)

### Development Setup

1. **Fork the Repository**
   ```bash
   # Fork the repo on GitHub and then clone your fork
   git clone https://github.com/your-username/AIStudy.git
   cd AIStudy
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your configuration
   
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

## 📝 Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes**: Help us identify and fix issues
- **Feature development**: Add new functionality
- **Documentation**: Improve existing docs or add new ones
- **Performance improvements**: Optimize code and algorithms
- **UI/UX enhancements**: Improve user experience
- **Testing**: Add or improve test coverage
- **AI model improvements**: Enhance AI capabilities

### Before You Start

1. **Check existing issues**: Look through open issues to see if your contribution is already being worked on
2. **Create an issue**: For new features or major changes, create an issue first to discuss the approach
3. **Small changes**: For minor fixes, you can directly create a pull request

## 🔄 Pull Request Process

### Creating a Pull Request

1. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   # or
   git checkout -b fix/bug-description
   ```

2. **Make your changes**
   - Follow the coding standards outlined below
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Backend tests
   cd backend
   python manage.py test
   
   # Frontend tests
   cd frontend
   npm test
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   # Use conventional commit messages (see below)
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Create a Pull Request**
   - Go to GitHub and create a pull request
   - Fill out the pull request template
   - Link any related issues

### Pull Request Guidelines

- **Clear title**: Use a descriptive title that summarizes the change
- **Detailed description**: Explain what you changed and why
- **Screenshots**: Include screenshots for UI changes
- **Testing**: Describe how you tested your changes
- **Breaking changes**: Clearly mark any breaking changes

### Commit Message Format

We use [Conventional Commits](https://conventionalcommits.org/) for commit messages:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

**Examples:**
```
feat(chatbot): add conversation history feature
fix(auth): resolve login token expiration issue
docs: update API documentation for new endpoints
style(frontend): fix linting issues in components
```

## 💻 Coding Standards

### Python (Backend)

- **Style**: Follow [PEP 8](https://pep8.org/) style guide
- **Imports**: Use absolute imports, group imports properly
- **Docstrings**: Use Google-style docstrings for functions and classes
- **Type hints**: Use type hints for function parameters and returns
- **Error handling**: Use proper exception handling

**Example:**
```python
from typing import List, Optional
from django.http import JsonResponse
from rest_framework import status


def get_user_courses(user_id: int) -> List[dict]:
    """
    Retrieve all courses for a specific user.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        List of course dictionaries
        
    Raises:
        User.DoesNotExist: If user is not found
    """
    try:
        user = User.objects.get(id=user_id)
        courses = user.courses.all()
        return [course.to_dict() for course in courses]
    except User.DoesNotExist:
        raise User.DoesNotExist(f"User with ID {user_id} not found")
```

### JavaScript/React (Frontend)

- **Style**: Use ESLint configuration provided
- **Components**: Use functional components with hooks
- **Props**: Use PropTypes or TypeScript for type checking
- **State management**: Use React Context or React Query appropriately
- **File naming**: Use PascalCase for components, camelCase for utilities

**Example:**
```javascript
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Box, Typography, CircularProgress } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const UserProfile = ({ userId }) => {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const { user } = useAuth();

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const response = await fetch(`/api/users/${userId}/profile/`);
                const data = await response.json();
                setProfile(data);
            } catch (error) {
                console.error('Error fetching profile:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchProfile();
    }, [userId]);

    if (loading) {
        return <CircularProgress />;
    }

    return (
        <Box>
            <Typography variant="h4">{profile?.name}</Typography>
            {/* Component content */}
        </Box>
    );
};

UserProfile.propTypes = {
    userId: PropTypes.number.isRequired,
};

export default UserProfile;
```

### Database Migrations

- **Always create migrations**: Use `makemigrations` for model changes
- **Review migrations**: Check generated migrations before committing
- **Data migrations**: Use data migrations for complex data transformations
- **Backwards compatibility**: Ensure migrations can be rolled back

## 🧪 Testing Guidelines

### Backend Testing

- **Unit tests**: Test individual functions and methods
- **Integration tests**: Test API endpoints and database interactions
- **Test coverage**: Aim for >80% test coverage
- **Test data**: Use factories or fixtures for test data

**Example:**
```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_user_registration(self):
        """Test user registration endpoint."""
        response = self.client.post('/api/auth/register/', self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())
        self.assertIn('tokens', response.data)
```

### Frontend Testing

- **Component tests**: Test React components with React Testing Library
- **Integration tests**: Test user interactions and API calls
- **Snapshot tests**: Use sparingly for stable components
- **Accessibility**: Test for accessibility compliance

**Example:**
```javascript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AuthProvider } from '../../contexts/AuthContext';
import LoginPage from '../LoginPage';

const renderWithProviders = (ui) => {
    return render(
        <AuthProvider>
            {ui}
        </AuthProvider>
    );
};

describe('LoginPage', () => {
    test('renders login form', () => {
        renderWithProviders(<LoginPage />);
        
        expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    });

    test('shows error for invalid credentials', async () => {
        renderWithProviders(<LoginPage />);
        
        fireEvent.change(screen.getByLabelText(/email/i), {
            target: { value: 'invalid@example.com' }
        });
        fireEvent.change(screen.getByLabelText(/password/i), {
            target: { value: 'wrongpassword' }
        });
        fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

        await waitFor(() => {
            expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
        });
    });
});
```

## 📚 Documentation

### Code Documentation

- **Inline comments**: Explain complex logic and business rules
- **Function/method docs**: Document parameters, return values, and exceptions
- **README updates**: Update README for significant changes
- **API documentation**: Update API docs for new endpoints

### Documentation Standards

- **Clear and concise**: Use simple language and avoid jargon
- **Examples**: Include code examples where helpful
- **Keep updated**: Ensure documentation stays current with code changes
- **Screenshots**: Include screenshots for UI changes

## 🐛 Issue Reporting

### Bug Reports

When reporting a bug, please include:

- **Clear title**: Summarize the issue in the title
- **Steps to reproduce**: Detailed steps to reproduce the bug
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: Browser, OS, Python/Node versions
- **Screenshots**: Include screenshots if applicable
- **Error logs**: Include relevant error messages

### Feature Requests

For feature requests, please include:

- **Problem statement**: What problem does this solve?
- **Proposed solution**: How would you like it to work?
- **Alternatives**: What alternatives have you considered?
- **Additional context**: Any other relevant information

## 🔄 Development Workflow

### Branch Naming Convention

- `feature/feature-name`: New features
- `fix/bug-description`: Bug fixes
- `docs/update-description`: Documentation updates
- `refactor/component-name`: Code refactoring
- `test/test-description`: Adding or updating tests

### Code Review Process

1. **Self-review**: Review your own code before submitting
2. **Automated checks**: Ensure all CI checks pass
3. **Peer review**: Address feedback from reviewers
4. **Approval**: Wait for approval from maintainers
5. **Merge**: Maintainers will merge approved PRs

### Release Process

- **Feature freeze**: No new features after feature freeze
- **Testing**: Thorough testing of release candidates
- **Documentation**: Update all relevant documentation
- **Release notes**: Comprehensive release notes for users

## 🎯 AI and ML Contributions

### AI Model Guidelines

- **Model documentation**: Document model architecture and training process
- **Performance metrics**: Include accuracy, precision, recall metrics
- **Data privacy**: Ensure compliance with data privacy regulations
- **Bias testing**: Test models for potential biases
- **Version control**: Use appropriate versioning for models

### Training Data

- **Data quality**: Ensure high-quality, diverse training data
- **Data sources**: Document data sources and licensing
- **Preprocessing**: Document data preprocessing steps
- **Validation**: Include proper train/validation/test splits

## 🏆 Recognition

Contributors will be recognized in:

- **Contributors list**: Added to the project contributors
- **Release notes**: Mentioned in relevant release notes
- **Hall of fame**: Featured contributors on project website
- **Badges**: GitHub badges for significant contributions

## 💬 Getting Help

If you need help with your contribution:

- **GitHub Issues**: Create an issue with the "question" label
- **Discord/Slack**: Join our community chat (if available)
- **Email**: Contact maintainers directly
- **Documentation**: Check existing documentation first

## 📄 License

By contributing to AIStudy, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

Thank you for contributing to AIStudy! Your efforts help make AI-powered education accessible to everyone. 🚀
