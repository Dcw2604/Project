"""
Interactive Exam Grading System

This module provides comprehensive grading and feedback for the adaptive testing system.
All feedback and explanations are provided in Hebrew.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from .adaptive_testing_engine import AdaptiveExamSession


@dataclass
class GradeBreakdown:
    """Detailed breakdown of student performance"""
    raw_score: int
    total_questions: int
    percentage: float
    difficulty_performance: Dict[str, Dict]
    mastery_level: str
    strengths: List[str]
    areas_for_improvement: List[str]
    personalized_feedback: str
    recommendations: List[str]


class ExamGradingSystem:
    """
    Comprehensive grading system for adaptive interactive exams
    All feedback provided in Hebrew
    """
    
    def __init__(self):
        self.difficulty_weights = {
            'easy': 1.0,
            'medium': 1.5,
            'hard': 2.0
        }
        
        self.mastery_thresholds = {
            'excellent': 90,    # מעולה
            'good': 75,         # טוב
            'satisfactory': 60, # מספק
            'needs_improvement': 0  # צריך שיפור
        }
    
    def calculate_final_grade(self, adaptive_session: AdaptiveExamSession) -> GradeBreakdown:
        """
        Calculate comprehensive final grade with Hebrew feedback using partial scores
        """
        # Calculate raw score using partial scores
        total_score = self._calculate_total_partial_score(adaptive_session)
        total_questions = adaptive_session.questions_answered
        
        # Calculate weighted score
        weighted_score = self._calculate_weighted_score(adaptive_session)
        
        # Calculate percentage based on partial scores
        percentage = (total_score / total_questions * 100) if total_questions > 0 else 0
        
        # Analyze difficulty performance
        difficulty_performance = self._analyze_difficulty_performance(adaptive_session)
        
        # Determine mastery level
        mastery_level = self._determine_mastery_level(percentage)
        
        # Generate feedback
        strengths = self._identify_strengths(difficulty_performance)
        areas_for_improvement = self._identify_improvement_areas(difficulty_performance)
        personalized_feedback = self._generate_personalized_feedback(
            mastery_level, difficulty_performance, adaptive_session
        )
        recommendations = self._generate_recommendations(difficulty_performance, mastery_level)
        
        return GradeBreakdown(
            raw_score=round(total_score, 1),
            total_questions=total_questions,
            percentage=round(percentage, 1),
            difficulty_performance=difficulty_performance,
            mastery_level=mastery_level,
            strengths=strengths,
            areas_for_improvement=areas_for_improvement,
            personalized_feedback=personalized_feedback,
            recommendations=recommendations
        )
    
    def _calculate_total_partial_score(self, session: AdaptiveExamSession) -> float:
        """Calculate total score using partial scores from attempts"""
        total_score = 0.0
        processed_questions = set()
        
        for attempt in session.question_attempts:
            if attempt.question_id not in processed_questions:
                # Get the best score for this question
                question_scores = [a.partial_score for a in session.question_attempts 
                                 if a.question_id == attempt.question_id]
                if question_scores:
                    total_score += max(question_scores)
                processed_questions.add(attempt.question_id)
        
        return total_score
    
    def _calculate_weighted_score(self, session: AdaptiveExamSession) -> float:
        """Calculate weighted score based on difficulty levels using partial scores"""
        weighted_total = 0
        max_weighted = 0
        
        for level, progress in session.difficulty_progress.items():
            if progress.questions_attempted > 0:
                weight = self.difficulty_weights.get(level, 1.0)
                # Calculate average partial score for this difficulty level
                level_attempts = [a for a in session.question_attempts if a.difficulty == level]
                if level_attempts:
                    level_scores = [a.partial_score for a in level_attempts]
                    avg_level_score = sum(level_scores) / len(level_scores)
                    weighted_total += avg_level_score * weight * progress.questions_attempted
                    max_weighted += weight * progress.questions_attempted
        
        return (weighted_total / max_weighted * 100) if max_weighted > 0 else 0
    
    def _analyze_difficulty_performance(self, session: AdaptiveExamSession) -> Dict[str, Dict]:
        """Analyze performance at each difficulty level using partial scores"""
        performance = {}
        
        for level, progress in session.difficulty_progress.items():
            if progress.questions_attempted > 0:
                # Calculate average partial score for this difficulty level
                level_attempts = [a for a in session.question_attempts if a.difficulty == level]
                if level_attempts:
                    level_scores = [a.partial_score for a in level_attempts]
                    avg_score = sum(level_scores) / len(level_scores)
                    accuracy = avg_score * 100
                else:
                    accuracy = (progress.correct_answers / progress.questions_attempted) * 100
                
                performance[level] = {
                    'questions_attempted': progress.questions_attempted,
                    'correct_answers': progress.correct_answers,
                    'accuracy': round(accuracy, 1),
                    'performance_level': self._get_performance_level(accuracy),
                    'hebrew_level': self._get_hebrew_difficulty_name(level)
                }
            else:
                performance[level] = {
                    'questions_attempted': 0,
                    'correct_answers': 0,
                    'accuracy': 0,
                    'performance_level': 'לא ניסה',
                    'hebrew_level': self._get_hebrew_difficulty_name(level)
                }
        
        return performance
    
    def _get_performance_level(self, accuracy: float) -> str:
        """Get Hebrew performance level description"""
        if accuracy >= 90:
            return "מעולה"
        elif accuracy >= 75:
            return "טוב מאוד"
        elif accuracy >= 60:
            return "טוב"
        elif accuracy >= 40:
            return "מספק"
        else:
            return "צריך שיפור"
    
    def _get_hebrew_difficulty_name(self, level: str) -> str:
        """Get Hebrew name for difficulty level"""
        names = {
            'easy': 'קל',
            'medium': 'בינוני',
            'hard': 'קשה'
        }
        return names.get(level, level)
    
    def _determine_mastery_level(self, percentage: float) -> str:
        """Determine overall mastery level in Hebrew"""
        if percentage >= 90:
            return "מעולה"
        elif percentage >= 75:
            return "טוב מאוד"
        elif percentage >= 60:
            return "טוב"
        else:
            return "צריך שיפור"
    
    def _identify_strengths(self, difficulty_performance: Dict) -> List[str]:
        """Identify student strengths in Hebrew"""
        strengths = []
        
        for level, perf in difficulty_performance.items():
            if perf['accuracy'] >= 80:
                strengths.append(f"הצלחה ברמת {perf['hebrew_level']} ({perf['accuracy']}%)")
        
        if not strengths:
            strengths.append("השלמת את המבחן בהתמדה")
        
        return strengths
    
    def _identify_improvement_areas(self, difficulty_performance: Dict) -> List[str]:
        """Identify areas for improvement in Hebrew"""
        areas = []
        
        for level, perf in difficulty_performance.items():
            if perf['accuracy'] < 60 and perf['questions_attempted'] > 0:
                areas.append(f"שיפור נדרש ברמת {perf['hebrew_level']} ({perf['accuracy']}%)")
        
        if not areas:
            areas.append("המשך לשמור על הרמה הגבוהה")
        
        return areas
    
    def _generate_personalized_feedback(self, mastery_level: str, difficulty_performance: Dict, 
                                      session: AdaptiveExamSession) -> str:
        """Generate personalized feedback in Hebrew"""
        feedback_parts = []
        
        # Overall performance
        feedback_parts.append(f"ביצועיך במבחן: {mastery_level}")
        
        # Difficulty-specific feedback
        for level, perf in difficulty_performance.items():
            if perf['questions_attempted'] > 0:
                if perf['accuracy'] >= 80:
                    feedback_parts.append(f"הצלחת מאוד ברמת {perf['hebrew_level']}")
                elif perf['accuracy'] >= 60:
                    feedback_parts.append(f"ביצוע טוב ברמת {perf['hebrew_level']}")
                else:
                    feedback_parts.append(f"יש מקום לשיפור ברמת {perf['hebrew_level']}")
        
        # Progression feedback
        if session.current_difficulty == 'hard':
            feedback_parts.append("הגעת לרמת הקושי הגבוהה ביותר - כל הכבוד!")
        elif session.current_difficulty == 'medium':
            feedback_parts.append("התקדמת לרמת הביניים - יפה מאוד!")
        
        # Time analysis
        if hasattr(session, 'question_attempts') and session.question_attempts:
            avg_time = sum(attempt.time_spent for attempt in session.question_attempts) / len(session.question_attempts)
            if avg_time < 30:
                feedback_parts.append("ענית מהר - זה מעיד על ביטחון בחומר")
            elif avg_time > 60:
                feedback_parts.append("לקחת זמן לחשוב - זה מעיד על חשיבה מעמיקה")
        
        return " ".join(feedback_parts)
    
    def _generate_recommendations(self, difficulty_performance: Dict, mastery_level: str) -> List[str]:
        """Generate study recommendations in Hebrew"""
        recommendations = []
        
        # General recommendations based on mastery level
        if mastery_level == "מעולה":
            recommendations.append("המשך לשמור על הרמה הגבוהה")
            recommendations.append("נסה אתגרים נוספים ברמת קושי גבוהה")
        elif mastery_level == "טוב מאוד":
            recommendations.append("אתה בדרך הנכונה - המשך כך")
            recommendations.append("נסה לחזק את האזורים החלשים יותר")
        elif mastery_level == "טוב":
            recommendations.append("יש לך בסיס טוב - המשך להתאמן")
            recommendations.append("התמקד בהבנה מעמיקה יותר של החומר")
        else:
            recommendations.append("התחל עם חומר ברמת קושי נמוכה יותר")
            recommendations.append("השתמש ברמזים כדי להבין טוב יותר")
        
        # Specific recommendations based on performance
        for level, perf in difficulty_performance.items():
            if perf['accuracy'] < 60 and perf['questions_attempted'] > 0:
                recommendations.append(f"התמקד יותר בחומר ברמת {perf['hebrew_level']}")
        
        return recommendations
    
    def generate_grade_report(self, adaptive_session: AdaptiveExamSession) -> Dict:
        """Generate complete grade report in Hebrew"""
        grade_breakdown = self.calculate_final_grade(adaptive_session)
        
        return {
            'summary': {
                'raw_score': f"{grade_breakdown.raw_score} מתוך {grade_breakdown.total_questions}",
                'percentage': f"{grade_breakdown.percentage}%",
                'mastery_level': grade_breakdown.mastery_level,
                'overall_feedback': grade_breakdown.personalized_feedback
            },
            'detailed_breakdown': {
                'difficulty_performance': grade_breakdown.difficulty_performance,
                'strengths': grade_breakdown.strengths,
                'areas_for_improvement': grade_breakdown.areas_for_improvement
            },
            'recommendations': grade_breakdown.recommendations,
            'next_steps': self._generate_next_steps(grade_breakdown),
            'encouragement': self._generate_encouragement_message(grade_breakdown)
        }
    
    def _generate_next_steps(self, grade_breakdown: GradeBreakdown) -> List[str]:
        """Generate next steps for the student"""
        next_steps = []
        
        if grade_breakdown.mastery_level == "מעולה":
            next_steps.append("נסה מבחנים ברמת קושי גבוהה יותר")
            next_steps.append("עזור לתלמידים אחרים")
        elif grade_breakdown.mastery_level in ["טוב מאוד", "טוב"]:
            next_steps.append("חזור על החומר החלש יותר")
            next_steps.append("נסה מבחן נוסף תוך שבוע")
        else:
            next_steps.append("חזור על החומר הבסיסי")
            next_steps.append("השתמש במשאבי למידה נוספים")
        
        return next_steps
    
    def _generate_encouragement_message(self, grade_breakdown: GradeBreakdown) -> str:
        """Generate encouraging message based on performance"""
        if grade_breakdown.percentage >= 90:
            return "🎉 ביצוע מעולה! אתה מוכן לאתגרים הבאים!"
        elif grade_breakdown.percentage >= 75:
            return "👏 ביצוע טוב מאוד! המשך כך!"
        elif grade_breakdown.percentage >= 60:
            return "👍 ביצוע טוב! יש לך בסיס מוצק להמשך הלמידה!"
        else:
            return "💪 כל צעד קדימה הוא חשוב! המשך להתאמן ותשתפר!"


# Global instance
exam_grading_system = ExamGradingSystem()
