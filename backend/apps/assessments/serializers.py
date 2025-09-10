from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.courses.models import Quiz, Course
from apps.progress.models import QuizResult

User = get_user_model()

class QuestionSerializer(serializers.Serializer):
    """Serializer for individual quiz questions"""
    id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=[
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
        ('fill_blank', 'Fill in the Blank')
    ])
    question = serializers.CharField(max_length=1000)
    options = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False,
        help_text="Options for multiple choice questions"
    )
    correct_answer = serializers.CharField(max_length=500, help_text="Correct answer or answer index")
    points = serializers.IntegerField(min_value=1, max_value=100, default=10)
    explanation = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    difficulty = serializers.ChoiceField(
        choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
        default='medium'
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        help_text="Tags for AI analysis and categorization"
    )

    def validate(self, data):
        """Validate question data based on type"""
        question_type = data.get('type')
        
        if question_type == 'multiple_choice':
            options = data.get('options', [])
            if len(options) < 2:
                raise serializers.ValidationError("Multiple choice questions must have at least 2 options")
            
            correct_answer = data.get('correct_answer')
            try:
                correct_index = int(correct_answer)
                if correct_index < 0 or correct_index >= len(options):
                    raise serializers.ValidationError("Correct answer index is out of range")
            except (ValueError, TypeError):
                raise serializers.ValidationError("For multiple choice, correct_answer must be an option index")
        
        elif question_type == 'true_false':
            correct_answer = data.get('correct_answer', '').lower()
            if correct_answer not in ['true', 'false', '1', '0']:
                raise serializers.ValidationError("True/False questions must have 'true' or 'false' as correct answer")
        
        return data


class QuizSerializer(serializers.ModelSerializer):
    """Main Quiz serializer for CRUD operations"""
    questions = QuestionSerializer(many=True, source='questions_data', required=False)
    total_questions = serializers.SerializerMethodField()
    total_points = serializers.SerializerMethodField()
    instructor_name = serializers.CharField(source='course.instructor.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    estimated_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'course', 'course_title', 'instructor_name',
            'questions', 'questions_data', 'total_questions', 'total_points',
            'passing_score', 'time_limit', 'attempts_allowed', 'show_results_immediately',
            'shuffle_questions', 'shuffle_options', 'estimated_duration',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'instructor_name', 'course_title']
    
    def get_total_questions(self, obj):
        """Calculate total number of questions"""
        if isinstance(obj.questions_data, list):
            return len(obj.questions_data)
        return 0
    
    def get_total_points(self, obj):
        """Calculate total points possible"""
        if isinstance(obj.questions_data, list):
            return sum(q.get('points', 10) for q in obj.questions_data)
        return 0
    
    def get_estimated_duration(self, obj):
        """Estimate quiz duration in minutes"""
        question_count = self.get_total_questions(obj)
        # Estimate 1.5 minutes per question on average
        return max(question_count * 1.5, 5)  # Minimum 5 minutes
    
    def validate_course(self, value):
        """Ensure user can create quiz for this course"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if user.role == 'teacher' and value.instructor != user:
                raise serializers.ValidationError("You can only create quizzes for your own courses")
        return value
    
    def validate_questions_data(self, value):
        """Validate questions data structure"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Questions data must be a list")
        
        if len(value) == 0:
            raise serializers.ValidationError("Quiz must have at least one question")
        
        # Validate each question using QuestionSerializer
        for i, question_data in enumerate(value):
            question_serializer = QuestionSerializer(data=question_data)
            if not question_serializer.is_valid():
                raise serializers.ValidationError(f"Question {i+1}: {question_serializer.errors}")
        
        return value
    
    def validate_passing_score(self, value):
        """Validate passing score is reasonable"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Passing score must be between 0 and 100")
        return value
    
    def create(self, validated_data):
        """Create quiz with proper data handling"""
        # Handle questions data
        questions_data = validated_data.pop('questions_data', [])
        
        # Assign unique IDs to questions if not present
        for i, question in enumerate(questions_data):
            if 'id' not in question:
                question['id'] = i + 1
        
        validated_data['questions_data'] = questions_data
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update quiz with proper data handling"""
        # Handle questions data
        questions_data = validated_data.pop('questions_data', instance.questions_data)
        
        # Ensure question IDs are maintained/assigned
        for i, question in enumerate(questions_data):
            if 'id' not in question:
                question['id'] = i + 1
        
        validated_data['questions_data'] = questions_data
        return super().update(instance, validated_data)


class QuizListSerializer(serializers.ModelSerializer):
    """Simplified serializer for quiz lists"""
    instructor_name = serializers.CharField(source='course.instructor.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    question_count = serializers.SerializerMethodField()
    total_points = serializers.SerializerMethodField()
    student_attempts = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'course', 'course_title', 'instructor_name',
            'question_count', 'total_points', 'passing_score', 'time_limit',
            'attempts_allowed', 'student_attempts', 'is_active', 'created_at'
        ]
    
    def get_question_count(self, obj):
        return len(obj.questions_data) if isinstance(obj.questions_data, list) else 0
    
    def get_total_points(self, obj):
        if isinstance(obj.questions_data, list):
            return sum(q.get('points', 10) for q in obj.questions_data)
        return 0
    
    def get_student_attempts(self, obj):
        """Get attempt count for current student"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.role == 'student':
            return QuizResult.objects.filter(
                quiz=obj,
                student=request.user
            ).count()
        return None


class StudentQuizSerializer(serializers.ModelSerializer):
    """Serializer for students taking quizzes (hides correct answers)"""
    questions = serializers.SerializerMethodField()
    course_title = serializers.CharField(source='course.title', read_only=True)
    instructor_name = serializers.CharField(source='course.instructor.get_full_name', read_only=True)
    question_count = serializers.SerializerMethodField()
    total_points = serializers.SerializerMethodField()
    student_attempts = serializers.SerializerMethodField()
    can_retake = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'course_title', 'instructor_name',
            'questions', 'question_count', 'total_points', 'passing_score',
            'time_limit', 'attempts_allowed', 'student_attempts', 'can_retake',
            'show_results_immediately', 'shuffle_questions', 'shuffle_options'
        ]
    
    def get_questions(self, obj):
        """Return questions without correct answers"""
        if not isinstance(obj.questions_data, list):
            return []
        
        student_questions = []
        for question in obj.questions_data:
            student_question = {
                'id': question.get('id'),
                'type': question.get('type'),
                'question': question.get('question'),
                'options': question.get('options', []),
                'points': question.get('points', 10),
                'tags': question.get('tags', [])
            }
            
            # Shuffle options if enabled
            if obj.shuffle_options and question.get('type') == 'multiple_choice':
                import random
                options = student_question['options'].copy()
                random.shuffle(options)
                student_question['options'] = options
            
            student_questions.append(student_question)
        
        # Shuffle questions if enabled
        if obj.shuffle_questions:
            import random
            random.shuffle(student_questions)
        
        return student_questions
    
    def get_question_count(self, obj):
        return len(obj.questions_data) if isinstance(obj.questions_data, list) else 0
    
    def get_total_points(self, obj):
        if isinstance(obj.questions_data, list):
            return sum(q.get('points', 10) for q in obj.questions_data)
        return 0
    
    def get_student_attempts(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return QuizResult.objects.filter(
                quiz=obj,
                student=request.user
            ).count()
        return 0
    
    def get_can_retake(self, obj):
        """Check if student can retake the quiz"""
        attempts = self.get_student_attempts(obj)
        return obj.attempts_allowed == 0 or attempts < obj.attempts_allowed
