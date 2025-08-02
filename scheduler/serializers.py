from rest_framework import serializers
from .models import Lesson, Document, QuestionBank, TestSession, StudentAnswer

from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data['role'],
            age=validated_data['age'],
            subject=validated_data['subject'],
            points=validated_data['role'],
            phone=validated_data['phone']
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
                 'score', 'passed', 'started_at', 'completed_at', 'answers']
        read_only_fields = ['id', 'started_at', 'completed_at', 'score', 'passed']

class TestSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSession
        fields = ['test_type', 'difficulty_level', 'subject', 'total_questions', 'time_limit_minutes']

