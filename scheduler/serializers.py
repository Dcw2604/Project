from rest_framework import serializers
from .models import Lesson, Document, QuestionBank, TestSession, StudentAnswer, ChatSession, ConversationMessage, ConversationInsight, LearningPath

from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'age', 'subject', 'phone']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data['role'],
            age=validated_data.get('age', 18),
            subject=validated_data.get('subject', ''),
            phone=validated_data.get('phone', 0)
        )
        return user
    

# Serializer that converts Lesson model instances to JSON and vice versa,
# enabling creation, retrieval, and update of lessons through the API
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

# Document serializers
class DocumentSerializer(serializers.ModelSerializer):
    preview = serializers.SerializerMethodField()
    text_length = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'document_type', 'file_path', 'processing_status', 'created_at', 'updated_at', 'preview', 'text_length']
        read_only_fields = ['id', 'created_at', 'updated_at', 'processing_status']
    
    def get_preview(self, obj):
        """Get a preview of the document text"""
        if obj.extracted_text:
            return obj.extracted_text[:200] + "..." if len(obj.extracted_text) > 200 else obj.extracted_text
        return "No content extracted yet"
    
    def get_text_length(self, obj):
        """Get the length of extracted text"""
        return len(obj.extracted_text) if obj.extracted_text else 0

class DocumentUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'document_type', 'file']
        read_only_fields = ['id']

# Question Bank serializers
class QuestionBankSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source='document.title', read_only=True)
    
    class Meta:
        model = QuestionBank
        fields = ['id', 'document', 'document_title', 'question_text', 'question_type', 
                 'difficulty_level', 'subject', 'option_a', 'option_b', 'option_c', 'option_d',
                 'correct_answer', 'explanation', 'is_approved', 'created_by_ai', 
                 'modified_by_teacher', 'created_at']
        read_only_fields = ['id', 'created_at', 'created_by_ai']

class QuestionBankCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = ['document', 'question_text', 'question_type', 'difficulty_level', 
                 'subject', 'option_a', 'option_b', 'option_c', 'option_d',
                 'correct_answer', 'explanation', 'is_approved']

# Exam serializers
class ExamCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    subject = serializers.CharField(required=False, allow_blank=True)
    difficulty_level = serializers.ChoiceField(choices=QuestionBank.DIFFICULTY_LEVELS, required=False, allow_null=True)
    total_questions = serializers.IntegerField(min_value=1)
    exam_time_limit_minutes = serializers.IntegerField(required=False, allow_null=True)
    per_question_time_seconds = serializers.IntegerField(required=False, allow_null=True)
    start_at = serializers.DateTimeField(required=False, allow_null=True)
    end_at = serializers.DateTimeField(required=False, allow_null=True)
    is_published = serializers.BooleanField(required=False)
    assigned_student_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    question_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    selection_rules = serializers.CharField(required=False, allow_blank=True)

class ExamSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    subject = serializers.CharField()
    difficulty_level = serializers.CharField(allow_blank=True)
    total_questions = serializers.IntegerField()
    exam_time_limit_minutes = serializers.IntegerField(allow_null=True)
    per_question_time_seconds = serializers.IntegerField(allow_null=True)
    start_at = serializers.DateTimeField(allow_null=True)
    end_at = serializers.DateTimeField(allow_null=True)
    is_published = serializers.BooleanField()
    assigned_students = serializers.ListField(child=serializers.CharField())
    question_ids = serializers.ListField(child=serializers.IntegerField())
    selection_rules = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField()

# Test Session serializers
class StudentAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    correct_answer = serializers.CharField(source='question.correct_answer', read_only=True)
    explanation = serializers.CharField(source='question.explanation', read_only=True)
    
    class Meta:
        model = StudentAnswer
        fields = ['id', 'question', 'question_text', 'student_answer', 'is_correct', 
                 'correct_answer', 'explanation', 'time_taken_seconds', 'answered_at']
        read_only_fields = ['id', 'answered_at', 'is_correct']

class TestSessionSerializer(serializers.ModelSerializer):
    answers = StudentAnswerSerializer(many=True, read_only=True)
    student_username = serializers.CharField(source='student.username', read_only=True)
    
    class Meta:
        model = TestSession
        fields = ['id', 'student', 'student_username', 'test_type', 'difficulty_level', 
                 'subject', 'total_questions', 'time_limit_minutes', 'is_completed', 
                 'score', 'passed', 'started_at', 'completed_at', 'answers', 'exam']
        read_only_fields = ['id', 'started_at', 'completed_at', 'score', 'passed']

class TestSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSession
        fields = ['test_type', 'difficulty_level', 'subject', 'total_questions', 'time_limit_minutes']


# =================
# INTERACTIVE LEARNING SERIALIZERS FOR SOCRATIC TUTORING
# =================

class ConversationMessageSerializer(serializers.ModelSerializer):
    """Serializer for individual conversation messages"""
    timestamp_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = ConversationMessage
        fields = ['id', 'message_type', 'content', 'sender', 'sentiment_score', 
                 'understanding_level', 'contains_question', 'shows_confusion', 
                 'shows_discovery', 'hint_level', 'timestamp', 'timestamp_formatted']
        read_only_fields = ['id', 'timestamp', 'sentiment_score', 'understanding_level', 
                           'contains_question', 'shows_confusion', 'shows_discovery']
    
    def get_timestamp_formatted(self, obj):
        """Return formatted timestamp for display"""
        return obj.timestamp.strftime('%H:%M:%S')


class ConversationInsightSerializer(serializers.ModelSerializer):
    """Serializer for conversation insights and analysis"""
    
    class Meta:
        model = ConversationInsight
        fields = ['id', 'insight_type', 'description', 'confidence_score', 
                 'recommendation', 'detected_at']
        read_only_fields = ['id', 'detected_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat learning sessions"""
    recent_messages = ConversationMessageSerializer(many=True, read_only=True, source='messages')
    student_username = serializers.CharField(source='student.username', read_only=True)
    current_question_text = serializers.CharField(source='current_question.question_text', read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    insights_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = ['id', 'student', 'student_username', 'session_type', 'topic', 'subject',
                 'learning_goal', 'current_understanding_level', 'status', 'total_messages',
                 'discoveries_made', 'current_question', 'current_question_text', 
                 'engagement_score', 'confusion_indicators', 'breakthrough_moments',
                 'started_at', 'last_activity', 'completed_at', 'duration_minutes',
                 'insights_count', 'recent_messages']
        read_only_fields = ['id', 'started_at', 'last_activity', 'total_messages', 
                           'discoveries_made', 'engagement_score', 'confusion_indicators', 
                           'breakthrough_moments']
    
    def get_duration_minutes(self, obj):
        """Calculate session duration in minutes"""
        if obj.completed_at:
            delta = obj.completed_at - obj.started_at
        else:
            from django.utils import timezone
            delta = timezone.now() - obj.started_at
        return int(delta.total_seconds() / 60)
    
    def get_insights_count(self, obj):
        """Count of insights generated for this session"""
        return obj.insights.count()


class ChatSessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new chat sessions"""
    
    class Meta:
        model = ChatSession
        fields = ['session_type', 'topic', 'subject', 'learning_goal', 'exam', 'current_question']


class LearningPathSerializer(serializers.ModelSerializer):
    """Serializer for adaptive learning paths"""
    student_username = serializers.CharField(source='student.username', read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    current_topic_display = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPath
        fields = ['id', 'student', 'student_username', 'subject', 'current_topic', 
                 'status', 'current_position', 'actual_progress_percent', 
                 'estimated_completion', 'created_at', 'last_updated',
                 'progress_percentage', 'current_topic_display']
        read_only_fields = ['id', 'created_at', 'last_updated']
    
    def get_progress_percentage(self, obj):
        """Format progress as percentage"""
        return f"{obj.actual_progress_percent:.1f}%"
    
    def get_current_topic_display(self, obj):
        """Display current topic with position info"""
        return f"{obj.current_topic} (Step {obj.current_position + 1})"


# Specialized serializers for API responses

class InteractiveLearningSessionResponseSerializer(serializers.Serializer):
    """Response format for starting interactive learning sessions"""
    session_id = serializers.IntegerField()
    welcome_message = serializers.CharField()
    topic = serializers.CharField()
    learning_goal = serializers.CharField()
    initial_question = serializers.CharField()


class ChatInteractionResponseSerializer(serializers.Serializer):
    """Response format for chat interactions"""
    ai_response = serializers.CharField()
    understanding_level = serializers.CharField(allow_null=True)
    hint_level = serializers.IntegerField(allow_null=True)
    discovery_detected = serializers.BooleanField()
    next_question = serializers.CharField(allow_null=True)
    session_complete = serializers.BooleanField()
    encouragement = serializers.CharField(allow_null=True)


class LearningProgressResponseSerializer(serializers.Serializer):
    """Response format for learning progress"""
    session_id = serializers.IntegerField()
    understanding_level = serializers.IntegerField()
    engagement_score = serializers.FloatField()
    discoveries_made = serializers.IntegerField()
    confusion_indicators = serializers.IntegerField()
    breakthrough_moments = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    recent_insights = ConversationInsightSerializer(many=True)
    learning_path_progress = serializers.CharField(allow_null=True)

