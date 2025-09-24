"""
Adaptive Testing Engine

This module implements an adaptive testing system that dynamically adjusts
question difficulty based on student performance:

1. Start with easy-level questions
2. 3 correct easy → move to medium-level questions  
3. 3 correct medium → move to hard questions (last 4)
4. Track all answers and performance
5. Store structured data for analysis
"""

import json
from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from django.utils import timezone


class DifficultyLevel(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class QuestionAttempt:
    """Represents a single attempt at answering a question"""
    question_id: int
    question_text: str
    difficulty: str
    student_answer: str
    correct_answer: str
    is_correct: bool
    attempt_number: int
    hints_used: List[str]
    time_spent: float  # in seconds
    timestamp: str


@dataclass
class DifficultyProgress:
    """Tracks progress within a difficulty level"""
    level: str
    questions_attempted: int
    correct_answers: int
    incorrect_answers: int
    current_streak: int
    required_streak: int = 3  # Need 3 correct to advance
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'level': self.level,
            'questions_attempted': self.questions_attempted,
            'correct_answers': self.correct_answers,
            'incorrect_answers': self.incorrect_answers,
            'current_streak': self.current_streak,
            'required_streak': self.required_streak
        }


@dataclass
class AdaptiveExamSession:
    """Complete adaptive exam session data"""
    session_id: int
    student_id: int
    exam_id: int
    start_time: str
    current_difficulty: str
    total_questions: int
    questions_answered: int
    difficulty_progress: Dict[str, DifficultyProgress]
    question_attempts: List[QuestionAttempt]
    exam_completed: bool
    final_score: float
    completion_time: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'session_id': self.session_id,
            'student_id': self.student_id,
            'exam_id': self.exam_id,
            'start_time': self.start_time,
            'current_difficulty': self.current_difficulty,
            'total_questions': self.total_questions,
            'questions_answered': self.questions_answered,
            'difficulty_progress': {k: v.to_dict() for k, v in self.difficulty_progress.items()},
            'question_attempts': [asdict(attempt) for attempt in self.question_attempts],
            'exam_completed': self.exam_completed,
            'final_score': self.final_score,
            'completion_time': self.completion_time
        }


class AdaptiveTestingEngine:
    """
    Adaptive Testing Engine that adjusts difficulty based on performance
    """
    
    def __init__(self):
        self.difficulty_requirements = {
            DifficultyLevel.EASY: 3,    # Need 3 correct to advance
            DifficultyLevel.MEDIUM: 3,  # Need 3 correct to advance
            DifficultyLevel.HARD: 4    # Last 4 questions are hard
        }
        
        self.difficulty_sequence = [
            DifficultyLevel.EASY,
            DifficultyLevel.MEDIUM, 
            DifficultyLevel.HARD
        ]
    
    def create_adaptive_session(self, session_id: int, student_id: int, exam_id: int) -> AdaptiveExamSession:
        """Create a new adaptive exam session"""
        return AdaptiveExamSession(
            session_id=session_id,
            student_id=student_id,
            exam_id=exam_id,
            start_time=timezone.now().isoformat(),
            current_difficulty=DifficultyLevel.EASY.value,
            total_questions=10,
            questions_answered=0,
            difficulty_progress={
                level.value: DifficultyProgress(
                    level=level.value,
                    questions_attempted=0,
                    correct_answers=0,
                    incorrect_answers=0,
                    current_streak=0,
                    required_streak=self.difficulty_requirements[level]
                )
                for level in self.difficulty_sequence
            },
            question_attempts=[],
            exam_completed=False,
            final_score=0.0
        )
    
    def record_answer(self, session: AdaptiveExamSession, question_id: int, 
                     question_text: str, student_answer: str, correct_answer: str,
                     is_correct: bool, hints_used: List[str] = None, 
                     time_spent: float = 0.0) -> Tuple[bool, str, Optional[str]]:
        """
        Record a student's answer and determine next action
        
        Returns:
            (should_advance_difficulty, next_difficulty, completion_status)
        """
        if hints_used is None:
            hints_used = []
        
        # Create attempt record
        attempt = QuestionAttempt(
            question_id=question_id,
            question_text=question_text,
            difficulty=session.current_difficulty,
            student_answer=student_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            attempt_number=len([a for a in session.question_attempts if a.question_id == question_id]) + 1,
            hints_used=hints_used,
            time_spent=time_spent,
            timestamp=timezone.now().isoformat()
        )
        
        # Add to session
        session.question_attempts.append(attempt)
        session.questions_answered += 1
        
        # Update difficulty progress
        progress = session.difficulty_progress[session.current_difficulty]
        progress.questions_attempted += 1
        
        if is_correct:
            progress.correct_answers += 1
            progress.current_streak += 1
        else:
            progress.incorrect_answers += 1
            progress.current_streak = 0  # Reset streak on incorrect answer
        
        # Check if we should advance difficulty
        should_advance, next_difficulty = self._check_difficulty_advancement(session)
        
        # Check if exam is completed
        if session.questions_answered >= session.total_questions:
            session.exam_completed = True
            session.completion_time = timezone.now().isoformat()
            session.final_score = self._calculate_final_score(session)
            return should_advance, next_difficulty, "completed"
        
        return should_advance, next_difficulty, None
    
    def _check_difficulty_advancement(self, session: AdaptiveExamSession) -> Tuple[bool, Optional[str]]:
        """Check if student should advance to next difficulty level"""
        current_progress = session.difficulty_progress[session.current_difficulty]
        
        # Check if we have enough correct answers in current difficulty
        if current_progress.current_streak >= current_progress.required_streak:
            # Find next difficulty level
            current_index = self.difficulty_sequence.index(DifficultyLevel(session.current_difficulty))
            
            if current_index < len(self.difficulty_sequence) - 1:
                next_difficulty = self.difficulty_sequence[current_index + 1]
                session.current_difficulty = next_difficulty.value
                return True, next_difficulty.value
            else:
                # Already at highest difficulty
                return False, None
        
        return False, None
    
    def _calculate_final_score(self, session: AdaptiveExamSession) -> float:
        """Calculate final score based on performance across all difficulties"""
        total_correct = sum(progress.correct_answers for progress in session.difficulty_progress.values())
        total_attempted = sum(progress.questions_attempted for progress in session.difficulty_progress.values())
        
        if total_attempted == 0:
            return 0.0
        
        # Weighted scoring: Easy=1, Medium=2, Hard=3
        weighted_score = 0
        total_weight = 0
        
        for level, progress in session.difficulty_progress.items():
            if progress.questions_attempted > 0:
                weight = {"easy": 1, "medium": 2, "hard": 3}[level]
                level_score = (progress.correct_answers / progress.questions_attempted) * weight
                weighted_score += level_score * progress.questions_attempted
                total_weight += weight * progress.questions_attempted
        
        return (weighted_score / total_weight) * 100 if total_weight > 0 else 0.0
    
    def get_adaptive_questions(self, session: AdaptiveExamSession, available_questions: List[Dict]) -> List[Dict]:
        """Get questions appropriate for current difficulty level"""
        current_difficulty = session.current_difficulty
        
        # Filter questions by difficulty
        difficulty_questions = [
            q for q in available_questions 
            if q.get('difficulty', 'medium') == current_difficulty
        ]
        
        # If not enough questions for current difficulty, use any available
        if len(difficulty_questions) < 3:
            difficulty_questions = available_questions
        
        return difficulty_questions
    
    def get_session_summary(self, session: AdaptiveExamSession) -> Dict:
        """Get comprehensive session summary"""
        return {
            'session_id': session.session_id,
            'student_id': session.student_id,
            'exam_id': session.exam_id,
            'start_time': session.start_time,
            'completion_time': session.completion_time,
            'exam_completed': session.exam_completed,
            'final_score': round(session.final_score, 2),
            'total_questions': session.total_questions,
            'questions_answered': session.questions_answered,
            'current_difficulty': session.current_difficulty,
            'difficulty_progress': {
                level: {
                    'questions_attempted': progress.questions_attempted,
                    'correct_answers': progress.correct_answers,
                    'incorrect_answers': progress.incorrect_answers,
                    'current_streak': progress.current_streak,
                    'required_streak': progress.required_streak,
                    'accuracy': round((progress.correct_answers / progress.questions_attempted * 100) if progress.questions_attempted > 0 else 0, 2)
                }
                for level, progress in session.difficulty_progress.items()
            },
            'question_attempts': [asdict(attempt) for attempt in session.question_attempts],
            'performance_analysis': self._analyze_performance(session)
        }
    
    def _analyze_performance(self, session: AdaptiveExamSession) -> Dict:
        """Analyze student performance patterns"""
        if not session.question_attempts:
            return {}
        
        # Calculate average time per question
        total_time = sum(attempt.time_spent for attempt in session.question_attempts)
        avg_time = total_time / len(session.question_attempts) if session.question_attempts else 0
        
        # Calculate hint usage
        total_hints = sum(len(attempt.hints_used) for attempt in session.question_attempts)
        avg_hints = total_hints / len(session.question_attempts) if session.question_attempts else 0
        
        # Find most challenging difficulty
        difficulty_accuracy = {}
        for level, progress in session.difficulty_progress.items():
            if progress.questions_attempted > 0:
                difficulty_accuracy[level] = progress.correct_answers / progress.questions_attempted
        
        most_challenging = min(difficulty_accuracy.items(), key=lambda x: x[1])[0] if difficulty_accuracy else None
        
        return {
            'average_time_per_question': round(avg_time, 2),
            'total_hints_used': total_hints,
            'average_hints_per_question': round(avg_hints, 2),
            'most_challenging_difficulty': most_challenging,
            'difficulty_accuracy': {k: round(v * 100, 2) for k, v in difficulty_accuracy.items()},
            'learning_curve': self._calculate_learning_curve(session)
        }
    
    def _calculate_learning_curve(self, session: AdaptiveExamSession) -> List[float]:
        """Calculate learning curve based on recent performance"""
        if len(session.question_attempts) < 3:
            return []
        
        # Calculate accuracy in groups of 3 questions
        curve = []
        for i in range(0, len(session.question_attempts), 3):
            group = session.question_attempts[i:i+3]
            if group:
                correct = sum(1 for attempt in group if attempt.is_correct)
                accuracy = correct / len(group)
                curve.append(round(accuracy * 100, 2))
        
        return curve
    
    def save_session_to_database(self, session: AdaptiveExamSession) -> bool:
        """Save adaptive session data to database"""
        try:
            from .models import StudentExamSession
            
            # Get or create the exam session
            exam_session, created = StudentExamSession.objects.get_or_create(
                id=session.session_id,
                defaults={
                    'student_id': session.student_id,
                    'exam_id': session.exam_id,
                    'status': 'completed' if session.exam_completed else 'in_progress',
                    'final_score': session.final_score,
                    'completed_at': timezone.now() if session.exam_completed else None
                }
            )
            
            # Store adaptive data in notes field
            adaptive_data = {
                'adaptive_session': asdict(session),
                'difficulty_progression': self._get_difficulty_progression(session),
                'performance_metrics': self._analyze_performance(session)
            }
            
            exam_session.notes = json.dumps(adaptive_data, ensure_ascii=False, indent=2)
            exam_session.save()
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving adaptive session: {e}")
            return False
    
    def _get_difficulty_progression(self, session: AdaptiveExamSession) -> List[Dict]:
        """Get the progression through difficulty levels"""
        progression = []
        
        for attempt in session.question_attempts:
            progression.append({
                'question_id': attempt.question_id,
                'difficulty': attempt.difficulty,
                'is_correct': attempt.is_correct,
                'timestamp': attempt.timestamp
            })
        
        return progression


# Global instance
adaptive_engine = AdaptiveTestingEngine()
