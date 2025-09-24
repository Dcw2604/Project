"""
Secure Data Handler

This module implements strict data handling rules for the exam system:
- Always separate teacher and student views
- Teacher mode: full dataset access
- Student mode: strict filtering by student_id
- Prevent cross-student data access
- Secure JSON file storage
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.core.exceptions import PermissionDenied
from .student_results_manager import student_results_manager


class SecureDataHandler:
    """
    Handles secure data access with strict separation between teacher and student views
    """
    
    def __init__(self):
        self.results_manager = student_results_manager
        self.secure_storage_path = self._get_secure_storage_path()
        self.ensure_secure_directory()
    
    def _get_secure_storage_path(self) -> str:
        """Get secure storage path for JSON files"""
        # Create a secure subdirectory within the project
        secure_dir = os.path.join(settings.BASE_DIR, 'secure_data')
        return secure_dir
    
    def ensure_secure_directory(self):
        """Ensure secure directory exists with proper permissions"""
        if not os.path.exists(self.secure_storage_path):
            os.makedirs(self.secure_storage_path, mode=0o700)  # Only owner can read/write/execute
        
        # Set secure permissions on the directory
        os.chmod(self.secure_storage_path, 0o700)
    
    def _validate_user_permissions(self, user_role: str, requested_student_id: int = None, 
                                 current_user_id: int = None) -> bool:
        """
        Validate user permissions based on role and requested data
        
        Rules:
        - Teachers: Can access all data
        - Students: Can only access their own data
        - Admins: Can access all data
        """
        if user_role in ['teacher', 'admin']:
            return True
        
        if user_role == 'student':
            if requested_student_id is None or current_user_id is None:
                return False
            return requested_student_id == current_user_id
        
        return False
    
    def _log_data_access(self, user_id: int, user_role: str, action: str, 
                        student_id: int = None, success: bool = True):
        """Log data access for security auditing"""
        log_entry = {
            'timestamp': str(datetime.now()),
            'user_id': user_id,
            'user_role': user_role,
            'action': action,
            'target_student_id': student_id,
            'success': success
        }
        
        # In production, this would go to a proper logging system
        print(f"🔒 Data Access Log: {json.dumps(log_entry, ensure_ascii=False)}")
    
    def get_teacher_data(self, user_id: int, user_role: str) -> Dict:
        """
        Teacher Mode: Full dataset access with comprehensive analytics
        
        Rules:
        - Only teachers and admins can access
        - Returns complete dataset
        - Includes all student data
        - Provides comprehensive analytics
        """
        # Validate permissions
        if not self._validate_user_permissions(user_role):
            self._log_data_access(user_id, user_role, 'teacher_data_access', success=False)
            raise PermissionDenied("רק מורים ומנהלים יכולים לגשת לנתוני המורה")
        
        try:
            # Get all results from secure storage
            all_results = self._load_secure_results()
            students = all_results.get('students', [])
            
            self._log_data_access(user_id, user_role, 'teacher_data_access', success=True)
            
            if not students:
                return {
                    'mode': 'teacher',
                    'message': 'אין תוצאות זמינות',
                    'data_security': 'full_access_granted',
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
                'data_security': 'full_access_granted',
                'summary': summary_stats,
                'difficulty_analysis': difficulty_analysis,
                'common_mistakes': common_mistakes,
                'individual_insights': individual_insights,
                'raw_data': students,  # Full access to all data
                'security_audit': {
                    'access_granted_to': 'all_students',
                    'data_filtering': 'none',
                    'permission_level': 'full'
                }
            }
            
        except Exception as e:
            self._log_data_access(user_id, user_role, 'teacher_data_access', success=False)
            raise Exception(f"שגיאה בטעינת נתוני המורה: {str(e)}")
    
    def get_student_data(self, user_id: int, user_role: str, requested_student_id: int) -> Dict:
        """
        Student Mode: Strict filtering by student_id
        
        Rules:
        - Students can only access their own data
        - Teachers can access any student's data
        - Strict filtering by student_id
        - No access to other students' data
        """
        # Validate permissions
        if not self._validate_user_permissions(user_role, requested_student_id, user_id):
            self._log_data_access(user_id, user_role, 'student_data_access', 
                                requested_student_id, success=False)
            raise PermissionDenied("אין לך הרשאה לגשת לנתונים אלה")
        
        try:
            # Load results from secure storage
            all_results = self._load_secure_results()
            students = all_results.get('students', [])
            
            # Strict filtering by student_id
            student_results = [s for s in students if s.get('student_id') == requested_student_id]
            
            self._log_data_access(user_id, user_role, 'student_data_access', 
                                requested_student_id, success=True)
            
            if not student_results:
                return {
                    'mode': 'student',
                    'student_id': requested_student_id,
                    'message': 'לא נמצאו תוצאות עבור התלמיד',
                    'data_security': 'filtered_by_student_id',
                    'error': 'STUDENT_NOT_FOUND',
                    'security_audit': {
                        'access_granted_to': f'student_{requested_student_id}_only',
                        'data_filtering': 'strict_student_id_filter',
                        'permission_level': 'restricted'
                    }
                }
            
            # Return only the most recent result for the student
            latest_result = student_results[-1]  # Most recent exam
            
            # Filter to show only personal data
            personal_data = {
                'mode': 'student',
                'student_id': requested_student_id,
                'data_security': 'filtered_by_student_id',
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
                },
                'security_audit': {
                    'access_granted_to': f'student_{requested_student_id}_only',
                    'data_filtering': 'strict_student_id_filter',
                    'permission_level': 'restricted',
                    'other_students_data': 'hidden'
                }
            }
            
            return personal_data
            
        except Exception as e:
            self._log_data_access(user_id, user_role, 'student_data_access', 
                                requested_student_id, success=False)
            raise Exception(f"שגיאה בטעינת נתוני התלמיד: {str(e)}")
    
    def save_secure_results(self, data: Dict) -> bool:
        """
        Save results to secure JSON file location
        
        Rules:
        - Save to secure directory with restricted permissions
        - Encrypt sensitive data if needed
        - Maintain data integrity
        """
        try:
            secure_file_path = os.path.join(self.secure_storage_path, 'student_results.json')
            
            # Add security metadata
            data['security_metadata'] = {
                'last_updated': str(datetime.now()),
                'storage_location': 'secure_directory',
                'access_restrictions': 'role_based',
                'data_encryption': 'none',  # In production, consider encryption
                'file_permissions': '0o600'  # Only owner can read/write
            }
            
            # Save to secure location
            with open(secure_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Set secure file permissions
            os.chmod(secure_file_path, 0o600)  # Only owner can read/write
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving secure results: {e}")
            return False
    
    def _load_secure_results(self) -> Dict:
        """Load results from secure JSON file location"""
        try:
            secure_file_path = os.path.join(self.secure_storage_path, 'student_results.json')
            
            if not os.path.exists(secure_file_path):
                return {"metadata": {}, "students": []}
            
            with open(secure_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"❌ Error loading secure results: {e}")
            return {"metadata": {}, "students": []}
    
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
        
        return {
            'total_students': total_students,
            'total_exams': total_exams,
            'average_score': round(average_score, 1),
            'performance_distribution': performance_dist
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
    
    def get_security_audit_log(self, user_id: int, user_role: str) -> Dict:
        """
        Get security audit log (teachers and admins only)
        
        Rules:
        - Only teachers and admins can access audit logs
        - Provides security monitoring capabilities
        """
        if user_role not in ['teacher', 'admin']:
            raise PermissionDenied("רק מורים ומנהלים יכולים לגשת ללוג האבטחה")
        
        # In production, this would return actual audit logs
        return {
            'audit_log': 'Security audit logs would be available here',
            'access_granted_to': f'user_{user_id}',
            'permission_level': 'admin'
        }


# Global instance
secure_data_handler = SecureDataHandler()
