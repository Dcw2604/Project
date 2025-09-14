"""
Student Results Manager

This module handles saving and managing student exam results in JSON format
for teacher analysis and reporting.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from django.conf import settings
from .models import StudentExamSession, StudentExamAnswer, InteractiveExamQuestion
from .adaptive_testing_engine import AdaptiveExamSession


class StudentResultsManager:
    """
    Manages student exam results storage in JSON format
    """
    
    def __init__(self):
        self.results_file = os.path.join(settings.BASE_DIR, 'student_results.json')
        self.ensure_results_file()
    
    def ensure_results_file(self):
        """Ensure the results file exists with proper structure"""
        if not os.path.exists(self.results_file):
            initial_data = {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0",
                    "description": "Student exam results storage"
                },
                "students": []
            }
            self.save_results(initial_data)
    
    def load_results(self) -> Dict:
        """Load existing results from JSON file"""
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading results file: {e}")
            return {"metadata": {}, "students": []}
    
    def save_results(self, data: Dict):
        """Save results to JSON file"""
        try:
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving results file: {e}")
    
    def extract_student_results(self, session: StudentExamSession, adaptive_session: AdaptiveExamSession) -> Dict:
        """
        Extract comprehensive student results from session and adaptive data
        """
        # Get all answers for this session
        answers = StudentExamAnswer.objects.filter(session=session).order_by('question__id')
        
        # Extract question details and answers
        question_answers = []
        for answer in answers:
            question_answers.append({
                "question_id": answer.question.id,
                "question_text": answer.question.question_text[:100] + "..." if len(answer.question.question_text) > 100 else answer.question.question_text,
                "difficulty": answer.question.difficulty,
                "student_answer": answer.final_answer,
                "correct_answer": answer.question.correct_answer,
                "is_correct": answer.is_correct,
                "partial_score": getattr(answer, 'partial_score', 0.0),
                "attempts_used": answer.attempts_used,
                "time_taken_seconds": answer.time_taken_seconds,
                "hints_used": [],  # No hints_used field in StudentExamAnswer model
                "gemini_evaluation": {
                    "correctness": getattr(answer, 'correctness', 'unknown'),
                    "feedback": getattr(answer, 'feedback', ''),
                    "gemini_response": getattr(answer, 'gemini_response', '')
                }
            })
        
        # Calculate difficulty performance
        difficulty_performance = {}
        for level, progress in adaptive_session.difficulty_progress.items():
            questions_attempted = getattr(progress, 'questions_attempted', 0) or 0
            correct_answers = getattr(progress, 'correct_answers', 0) or 0
            if questions_attempted > 0:
                accuracy = (correct_answers / questions_attempted) * 100
                difficulty_performance[level] = {
                    "questions_attempted": questions_attempted,
                    "correct_answers": correct_answers,
                    "accuracy": round(accuracy, 1),
                    "hebrew_level": self._get_hebrew_difficulty_name(level)
                }
        
        # Identify strengths and weaknesses
        strengths = self._identify_strengths(difficulty_performance)
        weaknesses = self._identify_weaknesses(difficulty_performance, question_answers)
        
        # Calculate final metrics
        total_questions = session.total_questions or 0
        questions_answered = session.questions_answered or 0
        correct_answers = session.correct_answers or 0
        final_score = session.final_score or 0.0
        percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Create student result record
        student_result = {
            "student_id": session.student.id,
            "student_username": session.student.username,
            "student_email": session.student.email,
            "exam_id": session.exam.id,
            "exam_title": session.exam.title,
            "session_id": session.id,
            "completion_timestamp": session.completed_at.isoformat() if session.completed_at else None,
            "total_questions": total_questions,
            "questions_answered": questions_answered,
            "correct_answers": correct_answers,
            "final_score": round(final_score, 2),
            "percentage": round(percentage, 1),
            "mastery_level": self._determine_mastery_level(percentage),
            "difficulty_reached": adaptive_session.current_difficulty,
            "difficulty_progression": {
                "started_at": "easy",
                "current_level": adaptive_session.current_difficulty,
                "advanced_to_medium": difficulty_performance.get('medium', {}).get('correct_answers', 0) >= 3,
                "advanced_to_hard": difficulty_performance.get('hard', {}).get('correct_answers', 0) >= 3
            },
            "difficulty_performance": difficulty_performance,
            "question_answers": question_answers,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "learning_analytics": {
                "average_time_per_question": self._calculate_average_time(question_answers),
                "total_hints_used": sum(len(qa.get("hints_used", [])) for qa in question_answers),
                "most_challenging_difficulty": self._find_most_challenging_difficulty(difficulty_performance),
                "learning_curve": self._calculate_learning_curve(question_answers)
            },
            "recommendations": self._generate_student_recommendations(difficulty_performance, percentage)
        }
        
        return student_result
    
    def save_student_results(self, session: StudentExamSession, adaptive_session: AdaptiveExamSession):
        """
        Save student results to JSON file
        """
        try:
            # Load existing results
            results_data = self.load_results()
            
            # Extract student results
            student_result = self.extract_student_results(session, adaptive_session)
            
            # Check if student already has results for this exam
            existing_index = None
            for i, existing_student in enumerate(results_data["students"]):
                if (existing_student["student_id"] == student_result["student_id"] and 
                    existing_student["exam_id"] == student_result["exam_id"]):
                    existing_index = i
                    break
            
            if existing_index is not None:
                # Update existing record
                results_data["students"][existing_index] = student_result
                print(f"Updated results for student {student_result['student_id']} in exam {student_result['exam_id']}")
            else:
                # Add new record
                results_data["students"].append(student_result)
                print(f"Added new results for student {student_result['student_id']} in exam {student_result['exam_id']}")
            
            # Update metadata
            results_data["metadata"]["last_updated"] = datetime.now().isoformat()
            results_data["metadata"]["total_students"] = len(results_data["students"])
            
            # Save to file
            self.save_results(results_data)
            
            return True
            
        except Exception as e:
            print(f"Error saving student results: {e}")
            return False
    
    def get_all_results(self) -> Dict:
        """Get all student results"""
        return self.load_results()
    
    def get_student_results(self, student_id: int) -> List[Dict]:
        """Get results for specific student"""
        results_data = self.load_results()
        return [student for student in results_data["students"] if student["student_id"] == student_id]
    
    def get_exam_results(self, exam_id: int) -> List[Dict]:
        """Get results for specific exam"""
        results_data = self.load_results()
        return [student for student in results_data["students"] if student["exam_id"] == exam_id]
    
    def get_teacher_analytics(self) -> Dict:
        """Get comprehensive analytics for teachers"""
        results_data = self.load_results()
        students = results_data["students"]
        
        if not students:
            return {
                "message": "No student results available",
                "overview": {
                    "total_students": 0,
                    "total_exams": 0,
                    "average_score": 0
                },
                "difficulty_analysis": {},
                "common_strengths": [],
                "common_weaknesses": [],
                "performance_distribution": {
                    "excellent": 0,
                    "good": 0,
                    "satisfactory": 0,
                    "needs_improvement": 0
                }
            }
        
        # Calculate overall statistics
        total_students = len(students)
        total_exams = len(set(student["exam_id"] for student in students))
        average_score = sum(student.get("percentage", 0) or 0 for student in students) / total_students
        
        # Difficulty analysis
        difficulty_stats = {}
        for student in students:
            for level, perf in student["difficulty_performance"].items():
                if level not in difficulty_stats:
                    difficulty_stats[level] = {"total_attempts": 0, "total_correct": 0, "students": 0}
                difficulty_stats[level]["total_attempts"] += perf.get("questions_attempted", 0) or 0
                difficulty_stats[level]["total_correct"] += perf.get("correct_answers", 0) or 0
                if (perf.get("questions_attempted", 0) or 0) > 0:
                    difficulty_stats[level]["students"] += 1
        
        # Calculate difficulty averages
        for level in difficulty_stats:
            if difficulty_stats[level]["students"] > 0:
                difficulty_stats[level]["average_accuracy"] = (
                    difficulty_stats[level]["total_correct"] / 
                    difficulty_stats[level]["total_attempts"] * 100
                )
        
        # Common strengths and weaknesses
        all_strengths = []
        all_weaknesses = []
        for student in students:
            all_strengths.extend(student.get("strengths", []) or [])
            all_weaknesses.extend(student.get("weaknesses", []) or [])
        
        return {
            "overview": {
                "total_students": total_students,
                "total_exams": total_exams,
                "average_score": round(average_score, 1),
                "date_range": {
                    "earliest": min((student.get("completion_timestamp") for student in students if student.get("completion_timestamp")), default=None),
                    "latest": max((student.get("completion_timestamp") for student in students if student.get("completion_timestamp")), default=None)
                }
            },
            "difficulty_analysis": difficulty_stats,
            "common_strengths": self._get_most_common_items(all_strengths),
            "common_weaknesses": self._get_most_common_items(all_weaknesses),
            "performance_distribution": self._calculate_performance_distribution(students)
        }
    
    def _get_hebrew_difficulty_name(self, level: str) -> str:
        """Get Hebrew name for difficulty level"""
        names = {
            'easy': 'קל',
            'medium': 'בינוני',
            'hard': 'קשה'
        }
        return names.get(level, level)
    
    def _identify_strengths(self, difficulty_performance: Dict) -> List[str]:
        """Identify student strengths"""
        strengths = []
        for level, perf in difficulty_performance.items():
            if perf["accuracy"] >= 80:
                strengths.append(f"הצלחה ברמת {perf['hebrew_level']} ({perf['accuracy']}%)")
        return strengths if strengths else ["השלמת המבחן בהתמדה"]
    
    def _identify_weaknesses(self, difficulty_performance: Dict, question_answers: List[Dict]) -> List[str]:
        """Identify student weaknesses"""
        weaknesses = []
        
        # Difficulty-based weaknesses
        for level, perf in difficulty_performance.items():
            if perf["accuracy"] < 60 and perf["questions_attempted"] > 0:
                weaknesses.append(f"קושי ברמת {perf['hebrew_level']} ({perf['accuracy']}%)")
        
        # Question-specific weaknesses
        incorrect_questions = [qa for qa in question_answers if not qa["is_correct"]]
        if len(incorrect_questions) > 3:
            weaknesses.append(f"קושי עם {len(incorrect_questions)} שאלות")
        
        return weaknesses if weaknesses else ["המשך לשמור על הרמה הגבוהה"]
    
    def _determine_mastery_level(self, percentage: float) -> str:
        """Determine mastery level in Hebrew"""
        if percentage >= 90:
            return "מעולה"
        elif percentage >= 75:
            return "טוב מאוד"
        elif percentage >= 60:
            return "טוב"
        else:
            return "צריך שיפור"
    
    def _calculate_average_time(self, question_answers: List[Dict]) -> float:
        """Calculate average time per question"""
        if not question_answers:
            return 0.0
        total_time = sum(qa.get("time_taken_seconds", 0) or 0 for qa in question_answers)
        return round(total_time / len(question_answers), 1)
    
    def _find_most_challenging_difficulty(self, difficulty_performance: Dict) -> str:
        """Find most challenging difficulty level"""
        if not difficulty_performance:
            return "לא זמין"
        
        min_accuracy = min(perf["accuracy"] for perf in difficulty_performance.values() if perf["questions_attempted"] > 0)
        for level, perf in difficulty_performance.items():
            if perf["questions_attempted"] > 0 and perf["accuracy"] == min_accuracy:
                return perf["hebrew_level"]
        return "לא זמין"
    
    def _calculate_learning_curve(self, question_answers: List[Dict]) -> List[float]:
        """Calculate learning curve based on question order"""
        if len(question_answers) < 2:
            return [100.0] if question_answers and question_answers[0]["is_correct"] else [0.0]
        
        curve = []
        correct_count = 0
        for i, qa in enumerate(question_answers):
            if qa["is_correct"]:
                correct_count += 1
            accuracy = (correct_count / (i + 1)) * 100
            curve.append(round(accuracy, 1))
        
        return curve
    
    def _generate_student_recommendations(self, difficulty_performance: Dict, percentage: float) -> List[str]:
        """Generate recommendations for student"""
        recommendations = []
        
        if percentage >= 90:
            recommendations.append("המשך לשמור על הרמה הגבוהה")
            recommendations.append("נסה אתגרים נוספים ברמת קושי גבוהה")
        elif percentage >= 75:
            recommendations.append("אתה בדרך הנכונה - המשך כך")
            recommendations.append("נסה לחזק את האזורים החלשים יותר")
        elif percentage >= 60:
            recommendations.append("יש לך בסיס טוב - המשך להתאמן")
            recommendations.append("התמקד בהבנה מעמיקה יותר של החומר")
        else:
            recommendations.append("התחל עם חומר ברמת קושי נמוכה יותר")
            recommendations.append("השתמש ברמזים כדי להבין טוב יותר")
        
        # Add difficulty-specific recommendations
        for level, perf in difficulty_performance.items():
            if perf["accuracy"] < 60 and perf["questions_attempted"] > 0:
                recommendations.append(f"התמקד יותר בחומר ברמת {perf['hebrew_level']}")
        
        return recommendations
    
    def _get_most_common_items(self, items: List[str], top_n: int = 5) -> List[Dict]:
        """Get most common items from list"""
        from collections import Counter
        counter = Counter(items)
        return [{"item": item, "count": count} for item, count in counter.most_common(top_n)]
    
    def _calculate_performance_distribution(self, students: List[Dict]) -> Dict:
        """Calculate performance distribution"""
        distribution = {
            "excellent": 0,  # 90%+
            "good": 0,       # 75-89%
            "satisfactory": 0, # 60-74%
            "needs_improvement": 0 # <60%
        }
        
        for student in students:
            percentage = student.get("percentage", 0) or 0
            if percentage >= 90:
                distribution["excellent"] += 1
            elif percentage >= 75:
                distribution["good"] += 1
            elif percentage >= 60:
                distribution["satisfactory"] += 1
            else:
                distribution["needs_improvement"] += 1
        
        return distribution


# Global instance
student_results_manager = StudentResultsManager()
