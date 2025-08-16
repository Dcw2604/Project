from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

# יצירת מודל של USER מוכן והוספת אופצית תפקיד 
class User(AbstractUser):
        ROLE_CHOICES = (
        ('student' , 'student'),
        ('teacher', 'teacher'),

        )
        role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
        age = models.IntegerField(default=18)
        points = models.IntegerField(default=0)
        subject = models.CharField(max_length=50, blank=True, null=True)
        phone = models.IntegerField(default=0)


class Lesson(models.Model):
    student = models.ForeignKey(User, on_delete= models.SET_NULL, null=True)  # taken from user management
    teacher = models.CharField(max_length=100, default='TBD')  # teacher name
    date = models.DateTimeField(null=True, blank=True)  # date and time of lesson
    duration = models.IntegerField(default=60)  # duration of the lesson
    subject = models.CharField(max_length=100, default='General')
    phone = models.IntegerField(default=0)
    status_CHOICES = (
        ('approved' , 'approved'),
        ('pending', 'pending'),
        ('cancelled','cancelled')

        )
    status = models.CharField(max_length=10, choices=status_CHOICES, default='pending')

#שמירה השיחות עם הצאט
class ChatInteraction(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role':'student'})
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

  # ניתוח עתידי
    topic = models.CharField(max_length=100, blank=True, null=True)  # למשל: "אלגברה", "גיאומטריה"
    difficulty_estimate = models.CharField(max_length=50, blank=True, null=True)  # למשל: "קל", "בינוני", "קשה"
    notes = models.TextField(blank=True, null=True)  # למשל תובנות מהצ'אט
    # Link to document if the question was about a document
    document = models.ForeignKey('Document', on_delete=models.SET_NULL, blank=True, null=True)
    
    # RAG context tracking
    context_used = models.BooleanField(default=False, help_text="Whether RAG context was used")
    sources_count = models.IntegerField(default=0, help_text="Number of document sources used")

    #הצגת המשתמש והשעה שבה הוא שלח הודעה
    def __str__(self):
        return f"{self.student.username} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

# Document storage for PDF files and other study materials
class Document(models.Model):
    DOCUMENT_TYPES = (
        ('pdf', 'PDF'),
        ('image', 'Image'), 
        ('text', 'Text'),
    )
    
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES)
    file_path = models.CharField(max_length=500)  # Store file path
    extracted_text = models.TextField(blank=True, null=True)  # Extracted text content
    metadata = models.TextField(blank=True, null=True)  # Store PDF metadata as JSON string
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Processing status
    PROCESSING_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    processing_status = models.CharField(max_length=15, choices=PROCESSING_STATUS, default='pending')
    processing_error = models.TextField(blank=True, null=True)
    
    # New fields for RAG and AI processing
    processed_content = models.TextField(blank=True, null=True, help_text="Extracted text content for AI processing")
    rag_chunks = models.TextField(blank=True, null=True, help_text="JSON stored RAG chunks")
    questions_generated_count = models.IntegerField(default=0, help_text="Number of questions generated from this document")
    
    def __str__(self):
        return f"{self.title} - {self.questions_generated_count} questions"
    
    class Meta:
        ordering = ['-created_at']

# Question Bank for storing generated questions from documents
class QuestionBank(models.Model):
    QUESTION_TYPES = (
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
    )
    
    DIFFICULTY_LEVELS = (
        ('3', 'Level 3 - Basic'),
        ('4', 'Level 4 - Intermediate'),
        ('5', 'Level 5 - Advanced'),
    )
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple_choice')
    difficulty_level = models.CharField(max_length=2, choices=DIFFICULTY_LEVELS)
    subject = models.CharField(max_length=100, default='math')
    
    # Topic relationship for exam filtering
    topic = models.ForeignKey('Topic', on_delete=models.SET_NULL, null=True, blank=True, 
                             related_name='questions', help_text="Topic category for this question")
    
    # For multiple choice questions
    option_a = models.TextField(blank=True, null=True)
    option_b = models.TextField(blank=True, null=True)
    option_c = models.TextField(blank=True, null=True)
    option_d = models.TextField(blank=True, null=True)
    
    correct_answer = models.TextField()  # Store the correct answer or option letter
    explanation = models.TextField(blank=True, null=True)  # RAG-generated explanation
    
    # Auto-generated or teacher-modified
    is_approved = models.BooleanField(default=True)
    created_by_ai = models.BooleanField(default=True)
    modified_by_teacher = models.BooleanField(default=False)
    is_generated = models.BooleanField(default=True, help_text="True if generated by AI/chat - used for exam filtering")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Q{self.id} - Level {self.difficulty_level} - {self.question_text[:50]}..."
    
    class Meta:
        ordering = ['difficulty_level', '-created_at']

# New model for teacher-created Exams
class Exam(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_exams', limit_choices_to={'role': 'teacher'})
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=100, default='math')
    # Optional default difficulty for sampling; exams can be mixed
    difficulty_level = models.CharField(max_length=2, choices=QuestionBank.DIFFICULTY_LEVELS, blank=True, null=True)

    total_questions = models.IntegerField(default=10)
    exam_time_limit_minutes = models.IntegerField(null=True, blank=True)
    per_question_time_seconds = models.IntegerField(null=True, blank=True)

    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

    # Assignments and question set
    assigned_students = models.ManyToManyField(User, blank=True, related_name='assigned_exams', limit_choices_to={'role': 'student'})
    questions = models.ManyToManyField(QuestionBank, blank=True, related_name='exams')

    # Selection rules for random sampling, e.g. {"difficulty": {"3": 5, "4": 5}, "subject": "math"}
    selection_rules = models.TextField(blank=True, null=True, help_text='Optional JSON rules for sampling questions')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Exam: {self.title} by {self.created_by.username}"

    class Meta:
        ordering = ['-created_at']

# Test Sessions for students
class TestSession(models.Model):
    TEST_TYPES = (
        ('level_test', 'Level Test'),
        ('practice_test', 'Practice Test'),
        ('exam', 'Exam'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_sessions')
    test_type = models.CharField(max_length=20, choices=TEST_TYPES)
    difficulty_level = models.CharField(max_length=2, choices=QuestionBank.DIFFICULTY_LEVELS)
    subject = models.CharField(max_length=100, default='math')
    
    # Link to exam when the session is created from a published exam
    exam = models.ForeignKey('Exam', on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    
    # Test configuration
    total_questions = models.IntegerField(default=10)
    time_limit_minutes = models.IntegerField(null=True, blank=True)  # Null for practice tests
    
    # Test status
    is_completed = models.BooleanField(default=False)
    score = models.FloatField(null=True, blank=True)
    passed = models.BooleanField(default=False)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.test_type} - Level {self.difficulty_level}"
    
    class Meta:
        ordering = ['-started_at']

# Individual answers for each question in a test session
class StudentAnswer(models.Model):
    # Support both test sessions and exam sessions
    test_session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name='answers', 
                                   null=True, blank=True)
    exam_session = models.ForeignKey('ExamSession', on_delete=models.CASCADE, related_name='student_answers', 
                                   null=True, blank=True)
    
    # Core fields
    question = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'},
                               help_text="Student who provided this answer", null=True, blank=True)
    answer_text = models.TextField(help_text="Student's answer text")
    
    # Answer evaluation
    is_correct = models.BooleanField(default=False)
    time_taken_seconds = models.IntegerField(null=True, blank=True)
    
    # Metadata and logs
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True,
                                   help_text="When the answer was submitted")
    interaction_log = models.TextField(default='{}', blank=True,
                                     help_text="JSON string of extra metadata from conversation/chat flow")
    
    # Legacy field for compatibility
    student_answer = models.TextField(help_text="Legacy field - use answer_text instead", 
                                    blank=True, null=True)
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
        # Ensure student can't answer same question twice in same session
        constraints = [
            models.UniqueConstraint(
                fields=['test_session', 'question', 'student'],
                condition=models.Q(test_session__isnull=False),
                name='unique_test_session_answer'
            ),
            models.UniqueConstraint(
                fields=['exam_session', 'question', 'student'],
                condition=models.Q(exam_session__isnull=False),
                name='unique_exam_session_answer'
            ),
            models.CheckConstraint(
                check=(
                    models.Q(test_session__isnull=False, exam_session__isnull=True) |
                    models.Q(test_session__isnull=True, exam_session__isnull=False)
                ),
                name='one_session_type_required'
            )
        ]
    
    def save(self, *args, **kwargs):
        # Ensure backward compatibility
        if not self.student_answer and self.answer_text:
            self.student_answer = self.answer_text
        elif not self.answer_text and self.student_answer:
            self.answer_text = self.student_answer
        super().save(*args, **kwargs)
    
    def __str__(self):
        session_type = "Test" if self.test_session else "Exam"
        session_id = self.test_session_id if self.test_session else self.exam_session_id
        return f"{self.student.username} - {session_type} {session_id} - Q{self.question.id} - {'✓' if self.is_correct else '✗'}"


# =================
# INTERACTIVE LEARNING MODELS FOR SOCRATIC TUTORING
# =================

class ChatSession(models.Model):
    """
    Tracks interactive learning sessions where students explore topics through conversation
    """
    SESSION_TYPES = (
        ('exam_chat', 'Exam Chat'),
        ('interactive_learning', 'Interactive Learning'),
        ('topic_exploration', 'Topic Exploration'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'), 
        ('paused', 'Paused'),
        ('abandoned', 'Abandoned'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='interactive_learning')
    topic = models.CharField(max_length=200, help_text="Main topic being explored")
    subject = models.CharField(max_length=100, default='math')
    
    # Learning objectives
    learning_goal = models.TextField(help_text="What the student should discover/understand")
    current_understanding_level = models.IntegerField(default=0, help_text="0-100 scale of understanding")
    
    # Session tracking
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    total_messages = models.IntegerField(default=0)
    discoveries_made = models.IntegerField(default=0, help_text="Number of 'aha' moments detected")
    
    # Linked to exam if this is exam-based learning
    exam = models.ForeignKey('Exam', on_delete=models.SET_NULL, null=True, blank=True)
    current_question = models.ForeignKey('QuestionBank', on_delete=models.SET_NULL, null=True, blank=True)
    
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Progress tracking
    engagement_score = models.FloatField(default=0.0, help_text="0-1 scale of student engagement")
    confusion_indicators = models.IntegerField(default=0, help_text="Count of confusion signals")
    breakthrough_moments = models.IntegerField(default=0, help_text="Major understanding breakthroughs")
    
    def __str__(self):
        return f"{self.student.username} - {self.topic} ({self.session_type})"
    
    class Meta:
        ordering = ['-started_at']


class ConversationMessage(models.Model):
    """
    Individual messages in a learning conversation with analysis
    """
    MESSAGE_TYPES = (
        ('student_question', 'Student Question'),
        ('student_answer', 'Student Answer'),
        ('ai_guidance', 'AI Guidance'),
        ('ai_question', 'AI Question'),
        ('hint', 'Hint'),
        ('encouragement', 'Encouragement'),
    )
    
    UNDERSTANDING_LEVELS = (
        ('confused', 'Confused'),
        ('partial', 'Partial Understanding'),
        ('good', 'Good Understanding'),
        ('mastery', 'Mastery'),
    )
    
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    content = models.TextField()
    sender = models.CharField(max_length=10, choices=[('student', 'Student'), ('ai', 'AI')])
    
    # Message analysis
    sentiment_score = models.FloatField(null=True, blank=True, help_text="TextBlob sentiment: -1 to 1")
    understanding_level = models.CharField(max_length=15, choices=UNDERSTANDING_LEVELS, null=True, blank=True)
    contains_question = models.BooleanField(default=False)
    shows_confusion = models.BooleanField(default=False)
    shows_discovery = models.BooleanField(default=False)
    
    # Response quality (for AI messages)
    led_to_discovery = models.BooleanField(default=False, help_text="Did this AI message lead to student discovery?")
    hint_level = models.IntegerField(null=True, blank=True, help_text="1-5 scale, 1=gentle nudge, 5=direct guidance")
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sender}: {self.content[:50]}... ({self.chat_session.topic})"
    
    class Meta:
        ordering = ['timestamp']


class ConversationInsight(models.Model):
    """
    AI analysis of conversation patterns and student learning progression
    """
    INSIGHT_TYPES = (
        ('breakthrough', 'Learning Breakthrough'),
        ('confusion_pattern', 'Confusion Pattern'),
        ('engagement_change', 'Engagement Change'),
        ('topic_mastery', 'Topic Mastery'),
        ('learning_style', 'Learning Style Indicator'),
    )
    
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='insights')
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPES)
    description = models.TextField(help_text="What was observed/discovered")
    confidence_score = models.FloatField(help_text="0-1 confidence in this insight")
    
    # Related messages that led to this insight
    trigger_messages = models.ManyToManyField(ConversationMessage, blank=True)
    
    # Actionable recommendations
    recommendation = models.TextField(blank=True, help_text="What should happen next based on this insight")
    
    detected_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.insight_type}: {self.description[:50]}..."
    
    class Meta:
        ordering = ['-detected_at']


class LearningPath(models.Model):
    """
    Adaptive learning path that evolves based on student conversations and discoveries
    """
    PATH_STATUS = (
        ('suggested', 'Suggested'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('modified', 'Modified'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_paths')
    subject = models.CharField(max_length=100, default='math')
    current_topic = models.CharField(max_length=200)
    
    # Path progression
    status = models.CharField(max_length=15, choices=PATH_STATUS, default='suggested')
    topics_sequence = models.TextField(help_text="JSON list of topics in learning order")
    current_position = models.IntegerField(default=0, help_text="Current position in sequence")
    
    # Adaptation factors
    student_strengths = models.TextField(blank=True, help_text="JSON list of identified strengths")
    areas_for_growth = models.TextField(blank=True, help_text="JSON list of areas needing work")
    learning_preferences = models.TextField(blank=True, help_text="JSON learning style preferences")
    
    # Milestones and progress
    milestones_achieved = models.TextField(blank=True, help_text="JSON list of completed milestones")
    estimated_completion = models.DateField(null=True, blank=True)
    actual_progress_percent = models.FloatField(default=0.0)
    
    # Linked sessions and insights
    chat_sessions = models.ManyToManyField(ChatSession, blank=True, related_name='learning_paths')
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.subject}: {self.current_topic}"
    
    class Meta:
        ordering = ['-last_updated']


class AdaptiveDifficultyTracker(models.Model):
    """
    Tracks student performance and adapts question difficulty dynamically
    """
    DIFFICULTY_LEVELS = (
        (1, 'Level 1 - Foundation'),
        (2, 'Level 2 - Basic'),
        (3, 'Level 3 - Intermediate'),
        (4, 'Level 4 - Advanced'),
        (5, 'Level 5 - Expert'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='difficulty_trackers')
    topic = models.CharField(max_length=200, help_text="Specific topic being learned")
    subject = models.CharField(max_length=100, default='math')
    
    # Current difficulty and progression
    current_difficulty = models.IntegerField(choices=DIFFICULTY_LEVELS, default=1, help_text="Current difficulty level")
    target_difficulty = models.IntegerField(choices=DIFFICULTY_LEVELS, default=3, help_text="Target difficulty to reach")
    
    # Performance metrics
    consecutive_successes = models.IntegerField(default=0, help_text="Consecutive correct answers")
    consecutive_failures = models.IntegerField(default=0, help_text="Consecutive incorrect answers")
    total_attempts = models.IntegerField(default=0)
    total_successes = models.IntegerField(default=0)
    
    # Progression rules
    success_threshold_to_advance = models.IntegerField(default=2, help_text="Consecutive successes needed to advance")
    failure_threshold_to_regress = models.IntegerField(default=3, help_text="Consecutive failures to regress difficulty")
    min_attempts_before_advance = models.IntegerField(default=3, help_text="Minimum attempts before advancing")
    
    # Confidence and mastery tracking
    confidence_score = models.FloatField(default=0.5, help_text="0-1 scale of student confidence")
    mastery_percentage = models.FloatField(default=0.0, help_text="0-100 scale of topic mastery")
    
    # Session tracking
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='difficulty_tracker', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def calculate_success_rate(self):
        """Calculate overall success rate"""
        if self.total_attempts == 0:
            return 0.0
        return (self.total_successes / self.total_attempts) * 100
    
    def should_advance_difficulty(self):
        """Determine if difficulty should be increased"""
        return (
            self.consecutive_successes >= self.success_threshold_to_advance and
            self.total_attempts >= self.min_attempts_before_advance and
            self.current_difficulty < self.target_difficulty
        )
    
    def should_regress_difficulty(self):
        """Determine if difficulty should be decreased"""
        return (
            self.consecutive_failures >= self.failure_threshold_to_regress and
            self.current_difficulty > 1
        )
    
    def update_performance(self, success, confidence_change=0):
        """Update performance metrics after a question attempt"""
        self.total_attempts += 1
        
        if success:
            self.total_successes += 1
            self.consecutive_successes += 1
            self.consecutive_failures = 0
            self.confidence_score = min(1.0, self.confidence_score + 0.1 + confidence_change)
        else:
            self.consecutive_successes = 0
            self.consecutive_failures += 1
            self.confidence_score = max(0.0, self.confidence_score - 0.1 + confidence_change)
        
        # Update mastery percentage
        self.mastery_percentage = min(100.0, (self.calculate_success_rate() + self.confidence_score * 20))
        
        # Auto-adjust difficulty
        if self.should_advance_difficulty():
            self.current_difficulty = min(5, self.current_difficulty + 1)
            self.consecutive_successes = 0  # Reset after advancing
        elif self.should_regress_difficulty():
            self.current_difficulty = max(1, self.current_difficulty - 1)
            self.consecutive_failures = 0  # Reset after regressing
        
        self.save()
        return self.current_difficulty
    
    def __str__(self):
        return f"{self.student.username} - {self.topic} - Level {self.current_difficulty} ({self.calculate_success_rate():.1f}% success)"
    
    class Meta:
        unique_together = ['student', 'topic', 'chat_session']
        ordering = ['-last_updated']


class QuestionAttempt(models.Model):
    """
    Records individual question attempts for detailed analytics
    """
    ATTEMPT_RESULTS = (
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect'),
        ('partial', 'Partially Correct'),
        ('skipped', 'Skipped'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_attempts')
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='question_attempts')
    difficulty_tracker = models.ForeignKey(AdaptiveDifficultyTracker, on_delete=models.CASCADE, related_name='attempts')
    
    # Question details
    question_text = models.TextField(help_text="The exact question asked")
    difficulty_level = models.IntegerField(choices=AdaptiveDifficultyTracker.DIFFICULTY_LEVELS)
    topic = models.CharField(max_length=200)
    
    # Student response
    student_answer = models.TextField()
    result = models.CharField(max_length=10, choices=ATTEMPT_RESULTS)
    time_taken_seconds = models.IntegerField(null=True, blank=True)
    
    # Context and analysis
    hint_level_used = models.IntegerField(default=0, help_text="0-5 scale of hints needed")
    confidence_before = models.FloatField(null=True, blank=True, help_text="Student confidence before attempt")
    confidence_after = models.FloatField(null=True, blank=True, help_text="Student confidence after attempt")
    
    # AI analysis
    understanding_demonstrated = models.TextField(blank=True, help_text="What understanding the student showed")
    misconceptions_identified = models.TextField(blank=True, help_text="Any misconceptions detected")
    
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.topic} L{self.difficulty_level} - {self.result}"
    
    class Meta:
        ordering = ['-attempted_at']


class LearningSession(models.Model):
    """Track structured learning sessions with step-by-step questions"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    topic = models.CharField(max_length=100)  # e.g., "Linear Equations", "Fractions"
    subject = models.CharField(max_length=50, default='Mathematics')
    
    # Session state
    current_question_index = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=10)
    is_completed = models.BooleanField(default=False)
    
    # Performance tracking
    correct_answers = models.IntegerField(default=0)
    total_attempts = models.IntegerField(default=0)
    understanding_level = models.IntegerField(default=0)  # 0-100%
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Assessment results for teacher
    strengths = models.TextField(blank=True, null=True)  # JSON of strong areas
    weaknesses = models.TextField(blank=True, null=True)  # JSON of weak areas
    recommendations = models.TextField(blank=True, null=True)  # What to focus on
    
    def __str__(self):
        return f"{self.student.username} - {self.topic} ({self.understanding_level}%)"

class QuestionResponse(models.Model):
    """Track individual question responses within a learning session"""
    session = models.ForeignKey(LearningSession, on_delete=models.CASCADE, related_name='responses')
    question_text = models.TextField()
    student_answer = models.TextField()
    is_correct = models.BooleanField()
    attempts_count = models.IntegerField(default=1)
    hint_level_reached = models.IntegerField(default=0)
    
    # AI feedback
    ai_feedback = models.TextField(blank=True, null=True)
    time_taken_seconds = models.IntegerField(default=0)
    
    # Skill assessment
    skill_demonstrated = models.CharField(max_length=100, blank=True, null=True)  # e.g., "algebraic_manipulation"
    difficulty_level = models.IntegerField(default=1)  # 1-5
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Q{self.session.current_question_index}: {'✓' if self.is_correct else '✗'}"


# ====================
# TASK 2.1: EXAM SESSION DEFINITION MODELS
# ====================

class Topic(models.Model):
    """Topic model to categorize questions"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=100, default='math')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class ExamSession(models.Model):
    """Teacher-defined exam session with specific configuration"""
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_exam_sessions', 
                                   limit_choices_to={'role': 'teacher'})
    title = models.CharField(max_length=200, help_text="Title of the exam session")
    description = models.TextField(blank=True, null=True, help_text="Optional description of the exam")
    num_questions = models.IntegerField(help_text="Total number of questions in this exam session")
    random_topic_distribution = models.BooleanField(default=False, 
                                                   help_text="If true, questions will be distributed randomly across all available topics")
    time_limit_seconds = models.IntegerField(null=True, blank=True, 
                                           help_text="Optional time limit per question in seconds")
    is_published = models.BooleanField(default=False, help_text="Whether the exam session is published and available to students")
    
    # Many-to-many relationships for manual selection
    selected_topics = models.ManyToManyField(Topic, blank=True, related_name='selected_exam_sessions',
                                           help_text="Topics selected for this exam session")
    manually_selected_questions = models.ManyToManyField(QuestionBank, blank=True, related_name='manual_exam_sessions',
                                                        help_text="Manually selected questions for this exam session")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.num_questions} questions by {self.created_by.username}"
    
    class Meta:
        ordering = ['-created_at']


class ExamSessionTopic(models.Model):
    """Many-to-many relationship between exam sessions and topics"""
    exam_session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='session_topics')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='exam_sessions')
    num_questions = models.IntegerField(default=1, help_text="Number of questions to select from this topic")
    
    class Meta:
        unique_together = ['exam_session', 'topic']
    
    def __str__(self):
        return f"Session {self.exam_session.id} - Topic: {self.topic.name} ({self.num_questions} questions)"


class ExamSessionQuestion(models.Model):
    """Questions assigned to an exam session with specific order and configuration"""
    exam_session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='session_questions')
    question = models.ForeignKey(QuestionBank, on_delete=models.CASCADE, related_name='exam_sessions')
    order_index = models.IntegerField(help_text="Sequential order of questions starting from 1")
    time_limit_seconds = models.IntegerField(null=True, blank=True, 
                                           help_text="Per-question time limit, overrides session default if set")
    
    class Meta:
        unique_together = ['exam_session', 'order_index']
        ordering = ['order_index']
    
    def __str__(self):
        return f"Session {self.exam_session.id} - Q{self.order_index}: {self.question.question_text[:50]}..."


class ExamAnswerAttempt(models.Model):
    """
    Track individual answer attempts during interactive exam sessions with OLAMA
    Each row represents one attempt by a student at answering a specific question
    """
    exam_session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='answer_attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_attempts', 
                               limit_choices_to={'role': 'student'})
    question = models.ForeignKey(QuestionBank, on_delete=models.CASCADE, related_name='answer_attempts')
    
    # Attempt tracking
    attempt_number = models.IntegerField(help_text="Which attempt this is (1, 2, 3, etc.)")
    answer_text = models.TextField(help_text="The student's answer for this attempt")
    is_correct = models.BooleanField(default=False, help_text="Whether this attempt was correct")
    
    # OLAMA interaction data
    hint_provided = models.TextField(blank=True, null=True, help_text="Hint provided by OLAMA after incorrect answer")
    olama_context = models.TextField(default='{}', help_text="JSON context for OLAMA conversation")
    
    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    time_taken_seconds = models.IntegerField(null=True, blank=True, help_text="Time taken for this attempt")
    
    class Meta:
        unique_together = ['exam_session', 'student', 'question', 'attempt_number']
        ordering = ['submitted_at']
    
    def __str__(self):
        return f"Attempt {self.attempt_number} by {self.student.username} - Q{self.question.id} - {'✓' if self.is_correct else '✗'}"


# ====================
# TASK 2.2: EXAM CONFIGURATION STORAGE MODELS
# ====================

class ExamConfig(models.Model):
    """
    Persistent exam configuration with metadata for scheduling and assignment
    Links to ExamSession and stores specific execution parameters
    """
    exam_session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='configurations',
                                   help_text="The exam session this configuration is based on")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_exam_configs',
                               limit_choices_to={'role': 'teacher'},
                               help_text="Teacher who created this configuration")
    assigned_student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_exam_configs',
                                        limit_choices_to={'role': 'student'}, null=True, blank=True,
                                        help_text="Optional student assignment for personalized exams")
    
    # Scheduling information
    start_time = models.DateTimeField(null=True, blank=True, 
                                     help_text="When the exam should become available to students")
    end_time = models.DateTimeField(null=True, blank=True,
                                   help_text="When the exam should no longer be available")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        """Validate that end_time is after start_time if both are provided"""
        from django.core.exceptions import ValidationError
        
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError({
                'end_time': 'End time must be after start time.'
            })
    
    def save(self, *args, **kwargs):
        """Run validation before saving"""
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        student_info = f" for {self.assigned_student.username}" if self.assigned_student else ""
        return f"Config for {self.exam_session.title}{student_info} by {self.teacher.username}"
    
    class Meta:
        ordering = ['-created_at']
        # Optional: prevent multiple configs for same session + student combination
        # unique_together = ['exam_session', 'assigned_student']


class ExamConfigQuestion(models.Model):
    """
    Ordered list of questions for a specific exam configuration
    Maintains the exact sequence and question selection for reproducible exams
    """
    exam_config = models.ForeignKey(ExamConfig, on_delete=models.CASCADE, related_name='config_questions',
                                   help_text="The exam configuration this question belongs to")
    question = models.ForeignKey(QuestionBank, on_delete=models.CASCADE, related_name='config_questions',
                                help_text="The question to include in this exam")
    order_index = models.PositiveIntegerField(help_text="Sequential order of questions starting from 1")
    
    class Meta:
        unique_together = [
            ['exam_config', 'order_index'],  # Ensure unique ordering per config
            ['exam_config', 'question']      # Prevent duplicate questions per config
        ]
        ordering = ['order_index']
    
    def __str__(self):
        return f"Config {self.exam_config.id} - Q{self.order_index}: {self.question.question_text[:50]}..."
