"""
Structured Interactive Learning System
Replaces traditional practice with AI-powered step-by-step questioning
Provides detailed assessment for teachers
"""
import json
import random
from datetime import datetime
from django.utils import timezone
from .models import LearningSession, QuestionResponse, User

class StructuredLearningManager:
    """Manages structured learning sessions with step-by-step questions"""
    
    def __init__(self, rag_processor):
        self.rag_processor = rag_processor
        self.question_banks = self._load_question_banks()
    
    def _load_question_banks(self):
        """Load structured question sets for different topics"""
        return {
            "Linear Equations": [
                {
                    "question": "Let's solve: 2x + 5 = 11. What does 'x' represent in this equation?",
                    "expected_concepts": ["variable", "unknown", "mystery number"],
                    "correct_answer_patterns": ["unknown", "variable", "number we need to find"],
                    "skill": "variable_recognition",
                    "difficulty": 1
                },
                {
                    "question": "To solve 2x + 5 = 11, what should we do to both sides first?",
                    "expected_concepts": ["subtract 5", "remove constant", "isolate"],
                    "correct_answer_patterns": ["subtract 5", "minus 5", "take away 5"],
                    "skill": "isolation_steps",
                    "difficulty": 2
                },
                {
                    "question": "After subtracting 5 from both sides, we get 2x = 6. What's the next step?",
                    "expected_concepts": ["divide by 2", "coefficient elimination"],
                    "correct_answer_patterns": ["divide by 2", "/2", "divide both sides by 2"],
                    "skill": "coefficient_elimination",
                    "difficulty": 2
                },
                {
                    "question": "We found x = 3. How can we verify this answer is correct?",
                    "expected_concepts": ["substitute", "check", "plug in"],
                    "correct_answer_patterns": ["substitute", "plug in", "check", "put back"],
                    "skill": "solution_verification",
                    "difficulty": 3
                },
                {
                    "question": "Let's check: 2(3) + 5 = ? What do you get?",
                    "expected_concepts": ["calculation", "arithmetic"],
                    "correct_answer_patterns": ["11", "2(3) + 5 = 11", "6 + 5 = 11"],
                    "skill": "arithmetic_verification",
                    "difficulty": 2
                }
            ],
            "Fractions": [
                {
                    "question": "What does 1/2 mean in simple terms?",
                    "expected_concepts": ["half", "one part of two", "division"],
                    "correct_answer_patterns": ["half", "one of two parts", "divide by 2"],
                    "skill": "fraction_meaning",
                    "difficulty": 1
                },
                {
                    "question": "If you have 3/4 of a pizza, how much pizza do you have?",
                    "expected_concepts": ["three quarters", "three parts of four"],
                    "correct_answer_patterns": ["three quarters", "3 out of 4 pieces", "most of it"],
                    "skill": "fraction_visualization",
                    "difficulty": 1
                }
            ]
        }
    
    def start_learning_session(self, student, topic, total_questions=10):
        """Start a new structured learning session"""
        session = LearningSession.objects.create(
            student=student,
            topic=topic,
            total_questions=min(total_questions, len(self.question_banks.get(topic, []))),
            current_question_index=0,
            understanding_level=0
        )
        
        print(f"🎓 Started learning session: {student.username} - {topic}")
        return session
    
    def get_current_question(self, session):
        """Get the current question for the session"""
        if session.current_question_index >= session.total_questions:
            return self._complete_session(session)
        
        questions = self.question_banks.get(session.topic, [])
        if session.current_question_index >= len(questions):
            return self._complete_session(session)
        
        current_q = questions[session.current_question_index]
        
        return {
            "question": current_q["question"],
            "question_number": session.current_question_index + 1,
            "total_questions": session.total_questions,
            "progress_percent": int((session.current_question_index / session.total_questions) * 100)
        }
    
    def process_student_answer(self, session, student_answer):
        """Process student's answer and provide feedback"""
        questions = self.question_banks.get(session.topic, [])
        current_q = questions[session.current_question_index]
        
        # Check if answer is correct
        is_correct = self._check_answer_correctness(student_answer, current_q)
        
        # Generate AI feedback
        ai_feedback = self._generate_ai_feedback(student_answer, current_q, is_correct)
        
        # Record the response
        response = QuestionResponse.objects.create(
            session=session,
            question_text=current_q["question"],
            student_answer=student_answer,
            is_correct=is_correct,
            ai_feedback=ai_feedback,
            skill_demonstrated=current_q["skill"],
            difficulty_level=current_q["difficulty"]
        )
        
        # Update session stats
        session.total_attempts += 1
        if is_correct:
            session.correct_answers += 1
            session.current_question_index += 1
            
        # Update understanding level
        session.understanding_level = int((session.correct_answers / session.total_attempts) * 100)
        session.save()
        
        return {
            "is_correct": is_correct,
            "feedback": ai_feedback,
            "next_question": self.get_current_question(session) if is_correct else None,
            "progress": {
                "correct": session.correct_answers,
                "total_attempts": session.total_attempts,
                "understanding": session.understanding_level
            }
        }
    
    def _check_answer_correctness(self, student_answer, question_data):
        """Check if student answer matches expected patterns"""
        answer_lower = student_answer.lower().strip()
        
        for pattern in question_data["correct_answer_patterns"]:
            if pattern.lower() in answer_lower:
                return True
        
        return False
    
    def _generate_ai_feedback(self, student_answer, question_data, is_correct):
        """Generate AI-powered feedback for student response"""
        if not self.rag_processor.llm:
            return self._get_fallback_feedback(is_correct)
        
        try:
            if is_correct:
                prompt = f"""Student correctly answered: "{student_answer}" for skill: {question_data['skill']}. 
                Generate brief encouraging feedback (max 15 words) and say "Let's move to the next question!"
                Be positive and specific about what they did well."""
            else:
                prompt = f"""Student answered: "{student_answer}" for question about {question_data['skill']}. 
                This was incorrect. Generate a helpful hint (max 20 words) to guide them toward the right answer.
                Don't give the answer directly, just guide them."""
            
            feedback = self.rag_processor.llm.invoke(prompt)
            return str(feedback).strip()[:150]  # Limit length
            
        except Exception as e:
            print(f"AI feedback generation failed: {e}")
            return self._get_fallback_feedback(is_correct)
    
    def _get_fallback_feedback(self, is_correct):
        """Fallback feedback when AI is unavailable"""
        if is_correct:
            return random.choice([
                "✅ Excellent! You got it right! Let's move to the next question!",
                "🎉 Perfect! You understand this concept! Moving on!",
                "👏 Great work! You're making excellent progress!"
            ])
        else:
            return random.choice([
                "Not quite right. Think about what the question is really asking.",
                "Good try! Consider the key concept we're working with here.",
                "Close! Look at the question again and think step by step."
            ])
    
    def _complete_session(self, session):
        """Complete the learning session and generate assessment"""
        session.is_completed = True
        session.completed_at = timezone.now()
        
        # Generate detailed assessment for teacher
        assessment = self._generate_teacher_assessment(session)
        session.strengths = assessment["strengths"]
        session.weaknesses = assessment["weaknesses"] 
        session.recommendations = assessment["recommendations"]
        session.save()
        
        return {
            "session_complete": True,
            "final_score": f"{session.correct_answers}/{session.total_attempts}",
            "understanding_level": session.understanding_level,
            "assessment": assessment
        }
    
    def _generate_teacher_assessment(self, session):
        """Generate detailed assessment for teacher review"""
        responses = session.responses.all()
        
        # Analyze by skill
        skills_performance = {}
        for response in responses:
            skill = response.skill_demonstrated
            if skill not in skills_performance:
                skills_performance[skill] = {"correct": 0, "total": 0}
            
            skills_performance[skill]["total"] += 1
            if response.is_correct:
                skills_performance[skill]["correct"] += 1
        
        # Determine strengths and weaknesses
        strengths = []
        weaknesses = []
        
        for skill, performance in skills_performance.items():
            success_rate = performance["correct"] / performance["total"]
            if success_rate >= 0.8:
                strengths.append(skill)
            elif success_rate < 0.6:
                weaknesses.append(skill)
        
        # Generate recommendations
        recommendations = []
        if weaknesses:
            recommendations.append(f"Focus on: {', '.join(weaknesses)}")
        if session.understanding_level < 70:
            recommendations.append("Needs additional practice with fundamentals")
        if session.understanding_level >= 85:
            recommendations.append("Ready for more advanced topics")
        
        return {
            "strengths": json.dumps(strengths),
            "weaknesses": json.dumps(weaknesses),
            "recommendations": json.dumps(recommendations),
            "skills_breakdown": skills_performance
        }
    
    def get_teacher_dashboard_data(self, teacher):
        """Get assessment data for teacher dashboard"""
        # Get all sessions for students in teacher's classes
        sessions = LearningSession.objects.filter(
            is_completed=True
        ).order_by('-completed_at')
        
        dashboard_data = []
        for session in sessions:
            dashboard_data.append({
                "student_name": session.student.username,
                "topic": session.topic,
                "score": f"{session.correct_answers}/{session.total_attempts}",
                "understanding_level": session.understanding_level,
                "strengths": json.loads(session.strengths or "[]"),
                "weaknesses": json.loads(session.weaknesses or "[]"),
                "recommendations": json.loads(session.recommendations or "[]"),
                "completed_at": session.completed_at.strftime("%Y-%m-%d %H:%M")
            })
        
        return dashboard_data
