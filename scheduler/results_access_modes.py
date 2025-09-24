"""
Results Access Modes

This module provides two different modes for accessing student exam results:
1. Teacher Mode - Full access to all data with comprehensive analytics
2. Student Mode - Limited access to personal data only
"""

import json
import os
from typing import Dict, List, Any, Optional
from django.conf import settings
from .student_results_manager import student_results_manager


class ResultsAccessModes:
    """
    Manages different access modes for exam results
    """
    
    def __init__(self):
        self.results_manager = student_results_manager
    
    def get_teacher_dashboard(self) -> Dict:
        """
        Teacher Mode: Comprehensive dashboard with all student data
        """
        try:
            # Get all results
            all_results = self.results_manager.get_all_results()
            students = all_results.get('students', [])
            
            if not students:
                return {
                    'mode': 'teacher',
                    'message': 'אין תוצאות זמינות',
                    'summary': {
                        'total_students': 0,
                        'total_exams': 0,
                        'average_score': 0
                    }
                }
            
            # Calculate comprehensive statistics
            summary_stats = self._calculate_teacher_summary(students)
            difficulty_analysis = self._analyze_difficulty_performance(students)
            common_mistakes = self._identify_common_mistakes(students)
            individual_insights = self._generate_individual_insights(students)
            
            return {
                'mode': 'teacher',
                'summary': summary_stats,
                'difficulty_analysis': difficulty_analysis,
                'common_mistakes': common_mistakes,
                'individual_insights': individual_insights,
                'raw_data': students  # Full access to all data
            }
            
        except Exception as e:
            return {
                'mode': 'teacher',
                'error': f'שגיאה בטעינת נתוני המורה: {str(e)}'
            }
    
    def get_student_results(self, student_id: int) -> Dict:
        """
        Student Mode: Personal results only
        """
        try:
            # Get results for specific student
            student_results = self.results_manager.get_student_results(student_id)
            
            if not student_results:
                return {
                    'mode': 'student',
                    'student_id': student_id,
                    'message': 'לא נמצאו תוצאות עבור התלמיד',
                    'error': 'STUDENT_NOT_FOUND'
                }
            
            # Return only the most recent result for the student
            latest_result = student_results[-1]  # Most recent exam
            
            # Filter to show only personal data
            personal_data = {
                'mode': 'student',
                'student_id': student_id,
                'student_name': latest_result.get('student_username', ''),
                'exam_info': {
                    'exam_title': latest_result.get('exam_title', ''),
                    'completion_date': latest_result.get('completion_timestamp', ''),
                    'total_questions': latest_result.get('total_questions', 0),
                    'questions_answered': latest_result.get('questions_answered', 0)
                },
                'performance': {
                    'correct_answers': latest_result.get('correct_answers', 0),
                    'total_questions': latest_result.get('total_questions', 0),
                    'final_score': latest_result.get('final_score', 0),
                    'percentage': latest_result.get('percentage', 0),
                    'mastery_level': latest_result.get('mastery_level', ''),
                    'difficulty_reached': latest_result.get('difficulty_reached', '')
                },
                'personal_insights': {
                    'strengths': latest_result.get('strengths', []),
                    'weaknesses': latest_result.get('weaknesses', []),
                    'recommendations': latest_result.get('recommendations', [])
                },
                'question_answers': self._format_student_answers(latest_result.get('question_answers', [])),
                'learning_analytics': {
                    'average_time_per_question': latest_result.get('learning_analytics', {}).get('average_time_per_question', 0),
                    'total_hints_used': latest_result.get('learning_analytics', {}).get('total_hints_used', 0),
                    'learning_curve': latest_result.get('learning_analytics', {}).get('learning_curve', [])
                }
            }
            
            return personal_data
            
        except Exception as e:
            return {
                'mode': 'student',
                'student_id': student_id,
                'error': f'שגיאה בטעינת נתוני התלמיד: {str(e)}'
            }
    
    def _calculate_teacher_summary(self, students: List[Dict]) -> Dict:
        """Calculate comprehensive summary statistics for teachers"""
        total_students = len(students)
        total_exams = len(set(student['exam_id'] for student in students))
        average_score = sum(student['percentage'] for student in students) / total_students if total_students > 0 else 0
        
        # Performance distribution
        performance_dist = {
            'excellent': len([s for s in students if s['percentage'] >= 90]),
            'good': len([s for s in students if 75 <= s['percentage'] < 90]),
            'satisfactory': len([s for s in students if 60 <= s['percentage'] < 75]),
            'needs_improvement': len([s for s in students if s['percentage'] < 60])
        }
        
        # Date range
        completion_dates = [s['completion_timestamp'] for s in students if s.get('completion_timestamp')]
        date_range = {
            'earliest': min(completion_dates) if completion_dates else None,
            'latest': max(completion_dates) if completion_dates else None
        }
        
        return {
            'total_students': total_students,
            'total_exams': total_exams,
            'average_score': round(average_score, 1),
            'performance_distribution': performance_dist,
            'date_range': date_range
        }
    
    def _analyze_difficulty_performance(self, students: List[Dict]) -> Dict:
        """Analyze performance by difficulty level"""
        difficulty_stats = {}
        
        for student in students:
            for level, perf in student.get('difficulty_performance', {}).items():
                if level not in difficulty_stats:
                    difficulty_stats[level] = {
                        'total_attempts': 0,
                        'total_correct': 0,
                        'students_attempted': 0,
                        'hebrew_name': perf.get('hebrew_level', level)
                    }
                
                difficulty_stats[level]['total_attempts'] += perf.get('questions_attempted', 0)
                difficulty_stats[level]['total_correct'] += perf.get('correct_answers', 0)
                if perf.get('questions_attempted', 0) > 0:
                    difficulty_stats[level]['students_attempted'] += 1
        
        # Calculate averages
        for level in difficulty_stats:
            if difficulty_stats[level]['total_attempts'] > 0:
                difficulty_stats[level]['average_accuracy'] = round(
                    (difficulty_stats[level]['total_correct'] / difficulty_stats[level]['total_attempts']) * 100, 1
                )
            else:
                difficulty_stats[level]['average_accuracy'] = 0
        
        return difficulty_stats
    
    def _identify_common_mistakes(self, students: List[Dict]) -> List[Dict]:
        """Identify questions with lowest accuracy across all students"""
        question_stats = {}
        
        for student in students:
            for answer in student.get('question_answers', []):
                question_id = answer.get('question_id')
                if question_id not in question_stats:
                    question_stats[question_id] = {
                        'question_text': answer.get('question_text', ''),
                        'difficulty': answer.get('difficulty', ''),
                        'total_attempts': 0,
                        'correct_attempts': 0
                    }
                
                question_stats[question_id]['total_attempts'] += 1
                if answer.get('is_correct', False):
                    question_stats[question_id]['correct_attempts'] += 1
        
        # Calculate accuracy for each question
        common_mistakes = []
        for question_id, stats in question_stats.items():
            if stats['total_attempts'] > 0:
                accuracy = (stats['correct_attempts'] / stats['total_attempts']) * 100
                common_mistakes.append({
                    'question_id': question_id,
                    'question_text': stats['question_text'][:100] + '...' if len(stats['question_text']) > 100 else stats['question_text'],
                    'difficulty': stats['difficulty'],
                    'accuracy': round(accuracy, 1),
                    'total_attempts': stats['total_attempts'],
                    'correct_attempts': stats['correct_attempts']
                })
        
        # Sort by accuracy (lowest first)
        common_mistakes.sort(key=lambda x: x['accuracy'])
        return common_mistakes[:10]  # Top 10 most difficult questions
    
    def _generate_individual_insights(self, students: List[Dict]) -> List[Dict]:
        """Generate insights for each individual student"""
        insights = []
        
        for student in students:
            insight = {
                'student_id': student['student_id'],
                'student_name': student.get('student_username', ''),
                'exam_title': student.get('exam_title', ''),
                'performance_summary': {
                    'score': f"{student.get('correct_answers', 0)}/{student.get('total_questions', 0)}",
                    'percentage': student.get('percentage', 0),
                    'mastery_level': student.get('mastery_level', ''),
                    'difficulty_reached': student.get('difficulty_reached', '')
                },
                'strengths': student.get('strengths', [])[:3],  # Top 3 strengths
                'weaknesses': student.get('weaknesses', [])[:3],  # Top 3 weaknesses
                'completion_date': student.get('completion_timestamp', '')
            }
            insights.append(insight)
        
        return insights
    
    def _format_student_answers(self, question_answers: List[Dict]) -> List[Dict]:
        """Format question answers for student display"""
        formatted_answers = []
        
        for i, answer in enumerate(question_answers, 1):
            formatted_answer = {
                'question_number': i,
                'question_text': answer.get('question_text', ''),
                'difficulty': answer.get('difficulty', ''),
                'student_answer': answer.get('student_answer', ''),
                'is_correct': answer.get('is_correct', False),
                'attempts_used': answer.get('attempts_used', 0),
                'time_taken': answer.get('time_taken_seconds', 0),
                'hints_used': answer.get('hints_used', [])
            }
            formatted_answers.append(formatted_answer)
        
        return formatted_answers
    
    def get_teacher_summary_report(self) -> Dict:
        """Generate a comprehensive summary report for teachers"""
        dashboard_data = self.get_teacher_dashboard()
        
        if 'error' in dashboard_data:
            return dashboard_data
        
        # Generate Hebrew summary report
        summary = dashboard_data['summary']
        difficulty_analysis = dashboard_data['difficulty_analysis']
        common_mistakes = dashboard_data['common_mistakes']
        
        report = {
            'report_title': 'דוח סיכום תוצאות מבחנים',
            'generated_at': '2025-09-12T15:00:00Z',  # This would be dynamic
            'overview': {
                'total_students': f"סה\"כ תלמידים: {summary['total_students']}",
                'total_exams': f"סה\"כ מבחנים: {summary['total_exams']}",
                'average_score': f"ציון ממוצע: {summary['average_score']}%"
            },
            'performance_distribution': {
                'excellent': f"מעולה (90%+): {summary['performance_distribution']['excellent']} תלמידים",
                'good': f"טוב מאוד (75-89%): {summary['performance_distribution']['good']} תלמידים",
                'satisfactory': f"טוב (60-74%): {summary['performance_distribution']['satisfactory']} תלמידים",
                'needs_improvement': f"צריך שיפור (<60%): {summary['performance_distribution']['needs_improvement']} תלמידים"
            },
            'difficulty_analysis': {
                level: f"רמת {stats['hebrew_name']}: {stats['average_accuracy']}% דיוק ({stats['students_attempted']} תלמידים)"
                for level, stats in difficulty_analysis.items()
            },
            'common_mistakes': [
                f"שאלה {mistake['question_id']}: {mistake['accuracy']}% דיוק ({mistake['total_attempts']} ניסיונות)"
                for mistake in common_mistakes[:5]
            ],
            'recommendations': self._generate_teacher_recommendations(summary, difficulty_analysis, common_mistakes)
        }
        
        return report
    
    def _generate_teacher_recommendations(self, summary: Dict, difficulty_analysis: Dict, common_mistakes: List[Dict]) -> List[str]:
        """Generate recommendations for teachers based on data analysis"""
        recommendations = []
        
        # Overall performance recommendations
        avg_score = summary['average_score']
        if avg_score >= 85:
            recommendations.append("הביצועים הכלליים מעולים - המשך עם הגישה הנוכחית")
        elif avg_score >= 70:
            recommendations.append("הביצועים טובים - שקול לחזק את האזורים החלשים יותר")
        else:
            recommendations.append("יש צורך בשיפור משמעותי - מומלץ לבדוק את שיטות ההוראה")
        
        # Difficulty-specific recommendations
        for level, stats in difficulty_analysis.items():
            if stats['average_accuracy'] < 60:
                recommendations.append(f"רמת {stats['hebrew_name']} דורשת תשומת לב מיוחדת - {stats['average_accuracy']}% דיוק")
        
        # Common mistakes recommendations
        if common_mistakes:
            high_difficulty_questions = [m for m in common_mistakes if m['accuracy'] < 50]
            if high_difficulty_questions:
                recommendations.append(f"יש {len(high_difficulty_questions)} שאלות עם דיוק נמוך מ-50% - מומלץ לחזור על החומר")
        
        return recommendations


# Global instance
results_access_modes = ResultsAccessModes()
