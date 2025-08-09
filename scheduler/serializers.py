from rest_framework import serializers
from .models import Lesson, Document, QuestionBank, TestSession, StudentAnswer, ChatSession, ConversationMessage, ConversationInsight, LearningPath, Topic, ExamSession, ExamSessionTopic, ExamSessionQuestion, ExamConfig, ExamConfigQuestion

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
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    topic_id = serializers.IntegerField(source='topic.id', read_only=True)
    
    class Meta:
        model = QuestionBank
        fields = ['id', 'document', 'document_title', 'topic', 'topic_id', 'topic_name',
                 'question_text', 'question_type', 'difficulty_level', 'subject', 
                 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 
                 'explanation', 'is_approved', 'created_by_ai', 'modified_by_teacher', 
                 'is_generated', 'created_at']
        read_only_fields = ['id', 'created_at', 'created_by_ai']

class QuestionBankCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = ['document', 'topic', 'question_text', 'question_type', 'difficulty_level', 
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


# ====================
# TASK 2.1: EXAM SESSION SERIALIZERS
# ====================

class TopicSerializer(serializers.ModelSerializer):
    """Serializer for Topic model"""
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'subject', 'question_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_question_count(self, obj):
        """Get count of chat-generated questions for this topic"""
        return obj.questions.filter(is_generated=True).count()


class ExamSessionQuestionSerializer(serializers.ModelSerializer):
    """Serializer for questions in an exam session"""
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    topic_id = serializers.IntegerField(source='question.topic.id', read_only=True)
    topic_name = serializers.CharField(source='question.topic.name', read_only=True)
    difficulty_level = serializers.CharField(source='question.difficulty_level', read_only=True)
    question_id = serializers.IntegerField(source='question.id', read_only=True)
    
    class Meta:
        model = ExamSessionQuestion
        fields = ['question_id', 'order_index', 'time_limit_seconds', 'question_text', 
                 'topic_id', 'topic_name', 'difficulty_level']


class ExamSessionTopicSerializer(serializers.ModelSerializer):
    """Serializer for topics in an exam session"""
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    topic_id = serializers.IntegerField(source='topic.id', read_only=True)
    
    class Meta:
        model = ExamSessionTopic
        fields = ['topic_id', 'topic_name']


class ExamSessionSerializer(serializers.ModelSerializer):
    """Serializer for exam session details"""
    topics = ExamSessionTopicSerializer(source='session_topics', many=True, read_only=True)
    questions = ExamSessionQuestionSerializer(source='session_questions', many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ExamSession
        fields = ['id', 'created_by', 'created_by_username', 'num_questions', 
                 'random_topic_distribution', 'time_limit_seconds', 'created_at', 
                 'updated_at', 'topics', 'questions']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class ExamSessionCreateSerializer(serializers.Serializer):
    """Serializer for creating new exam sessions"""
    title = serializers.CharField(max_length=200, help_text="Title of the exam session")
    description = serializers.CharField(required=False, allow_blank=True, help_text="Optional description")
    num_questions = serializers.IntegerField(min_value=1, help_text="Total number of questions")
    topic_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        help_text="List of topic IDs to include questions from"
    )
    random_topic_distribution = serializers.BooleanField(
        default=False,
        help_text="If true, ignore topic_ids and distribute questions randomly across all topics"
    )
    time_limit_seconds = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        help_text="Optional time limit per question in seconds"
    )
    is_published = serializers.BooleanField(default=False, help_text="Whether to publish immediately")
    selected_question_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        help_text="Manually selected question IDs (these will be included first)"
    )
    
    def validate(self, data):
        """Custom validation for exam session creation"""
        random_topic = data.get('random_topic_distribution', False)
        topic_ids = data.get('topic_ids', [])
        selected_question_ids = data.get('selected_question_ids', [])
        
        # If not random distribution and no topics provided and no manual selections, it's invalid
        if not random_topic and not topic_ids and not selected_question_ids:
            raise serializers.ValidationError(
                "Either set random_topic_distribution=true, provide topic_ids, or provide selected_question_ids"
            )
        
        # Validate that selected questions exist and are chat-generated
        if selected_question_ids:
            valid_questions = QuestionBank.objects.filter(
                id__in=selected_question_ids,
                is_generated=True  # Only chat-generated questions allowed
            ).count()
            
            if valid_questions != len(selected_question_ids):
                raise serializers.ValidationError(
                    "All selected_question_ids must belong to chat-generated questions"
                )
        
        return data


# ====================
# TASK 2.2: EXAM CONFIGURATION SERIALIZERS
# ====================

class ExamConfigQuestionWriteSerializer(serializers.Serializer):
    """Serializer for writing exam config questions (incoming data)"""
    question_id = serializers.IntegerField(help_text="ID of the question to include")
    order_index = serializers.IntegerField(min_value=1, help_text="Order position starting from 1")


class ExamConfigQuestionReadSerializer(serializers.ModelSerializer):
    """Serializer for reading exam config questions (response data)"""
    question_id = serializers.IntegerField(source='question.id', read_only=True)
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    topic_name = serializers.CharField(source='question.topic.name', read_only=True)
    difficulty_level = serializers.CharField(source='question.difficulty_level', read_only=True)
    
    class Meta:
        model = ExamConfigQuestion
        fields = ['id', 'question_id', 'question_text', 'topic_name', 'difficulty_level', 'order_index']
        read_only_fields = ['id']


class ExamConfigSerializer(serializers.ModelSerializer):
    """
    Serializer for exam configurations with write + read support
    Handles creation and retrieval of complete exam configurations
    """
    # Write fields (for incoming requests)
    exam_session_id = serializers.IntegerField(write_only=True, help_text="ID of the exam session")
    teacher_id = serializers.IntegerField(write_only=True, help_text="ID of the teacher creating the config")
    assigned_student_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True,
        help_text="Optional ID of assigned student"
    )
    questions = ExamConfigQuestionWriteSerializer(many=True, write_only=True, help_text="List of questions with order")
    
    # Read fields (for responses)
    teacher = serializers.SerializerMethodField(read_only=True)
    assigned_student = serializers.SerializerMethodField(read_only=True)
    exam_session = serializers.SerializerMethodField(read_only=True)
    config_questions = ExamConfigQuestionReadSerializer(many=True, read_only=True)
    
    class Meta:
        model = ExamConfig
        fields = [
            'id', 'exam_session_id', 'teacher_id', 'assigned_student_id',
            'start_time', 'end_time', 'questions',
            'teacher', 'assigned_student', 'exam_session', 'config_questions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_teacher(self, obj):
        """Return teacher information"""
        return {
            'id': obj.teacher.id,
            'username': obj.teacher.username,
            'email': obj.teacher.email
        }
    
    def get_assigned_student(self, obj):
        """Return assigned student information if exists"""
        if obj.assigned_student:
            return {
                'id': obj.assigned_student.id,
                'username': obj.assigned_student.username,
                'email': obj.assigned_student.email
            }
        return None
    
    def get_exam_session(self, obj):
        """Return basic exam session information"""
        return {
            'id': obj.exam_session.id,
            'title': obj.exam_session.title,
            'description': obj.exam_session.description,
            'num_questions': obj.exam_session.num_questions
        }
    
    def validate(self, data):
        """Custom validation for exam configuration creation"""
        from .models import ExamSession, User, QuestionBank
        
        # Validate exam session exists
        exam_session_id = data.get('exam_session_id')
        if not ExamSession.objects.filter(id=exam_session_id).exists():
            raise serializers.ValidationError({
                'exam_session_id': 'Exam session does not exist.'
            })
        
        # Validate teacher exists and has correct role
        teacher_id = data.get('teacher_id')
        try:
            teacher = User.objects.get(id=teacher_id, role='teacher')
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'teacher_id': 'Teacher does not exist or is not a teacher.'
            })
        
        # Validate assigned student if provided
        assigned_student_id = data.get('assigned_student_id')
        if assigned_student_id:
            try:
                User.objects.get(id=assigned_student_id, role='student')
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'assigned_student_id': 'Student does not exist or is not a student.'
                })
        
        # Validate questions
        questions = data.get('questions', [])
        if not questions:
            raise serializers.ValidationError({
                'questions': 'At least one question is required.'
            })
        
        # Validate question order indices are contiguous starting from 1
        order_indices = [q['order_index'] for q in questions]
        expected_indices = list(range(1, len(questions) + 1))
        if sorted(order_indices) != expected_indices:
            raise serializers.ValidationError({
                'questions': 'Order indices must be contiguous starting from 1.'
            })
        
        # Validate all questions exist
        question_ids = [q['question_id'] for q in questions]
        existing_questions = QuestionBank.objects.filter(id__in=question_ids).count()
        if existing_questions != len(question_ids):
            raise serializers.ValidationError({
                'questions': 'Some questions do not exist.'
            })
        
        # Validate time constraints
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({
                'end_time': 'End time must be after start time.'
            })
        
        return data
    
    def create(self, validated_data):
        """Create exam configuration with ordered questions"""
        from .models import ExamSession, User, QuestionBank, ExamConfigQuestion
        
        # Extract nested data
        questions_data = validated_data.pop('questions')
        exam_session_id = validated_data.pop('exam_session_id')
        teacher_id = validated_data.pop('teacher_id')
        assigned_student_id = validated_data.pop('assigned_student_id', None)
        
        # Get related objects
        exam_session = ExamSession.objects.get(id=exam_session_id)
        teacher = User.objects.get(id=teacher_id)
        assigned_student = User.objects.get(id=assigned_student_id) if assigned_student_id else None
        
        # Create exam config
        exam_config = ExamConfig.objects.create(
            exam_session=exam_session,
            teacher=teacher,
            assigned_student=assigned_student,
            **validated_data
        )
        
        # Create ordered questions
        config_questions = []
        for question_data in questions_data:
            question = QuestionBank.objects.get(id=question_data['question_id'])
            config_questions.append(
                ExamConfigQuestion(
                    exam_config=exam_config,
                    question=question,
                    order_index=question_data['order_index']
                )
            )
        
        # Bulk create for efficiency
        ExamConfigQuestion.objects.bulk_create(config_questions)
        
        return exam_config

