import json
import logging
from typing import List, Dict, Any
from .models import Topic, QuestionTopic, QuestionBank

logger = logging.getLogger(__name__)

class TopicExtractor:
    def __init__(self):
        # רשימת נושאים ידועים במדעי המחשב
        self.common_topics = [
            "Algorithms", "Data Structures", "Complexity Analysis", 
            "Graphs", "Trees", "Sorting", "Searching", "Recursion",
            "Dynamic Programming", "Greedy Algorithms", "Hash Tables",
            "Linked Lists", "Arrays", "Stacks", "Queues", "Binary Search",
            "Heap", "Binary Tree", "BST", "Graph Traversal", "Shortest Path"
        ]
    
    def extract_topics_from_question(self, question_text: str) -> List[str]:
        """מזהה נושאים מהשאלה"""
        topics = []
        question_lower = question_text.lower()
        
        # חיפוש נושאים ידועים
        for topic in self.common_topics:
            if self._is_topic_in_question(topic.lower(), question_lower):
                topics.append(topic)
        
        # אם לא מצאנו נושאים, ננסה לזהות לפי מילות מפתח
        if not topics:
            topics = self._extract_by_keywords(question_text)
        
        return topics[:3]  # מקסימום 3 נושאים
    
    def _is_topic_in_question(self, topic: str, question_lower: str) -> bool:
        """בודק אם נושא נמצא בשאלה"""
        topic_words = topic.split()
        
        # חיפוש מדויק
        if topic in question_lower:
            return True
        
        # חיפוש חלקי (לפחות 70% מהמילים)
        if len(topic_words) > 1:
            matches = sum(1 for word in topic_words if word in question_lower)
            return matches / len(topic_words) >= 0.7
        
        return False
    
    def _extract_by_keywords(self, question_text: str) -> List[str]:
        """מזהה נושאים לפי מילות מפתח"""
        keyword_mapping = {
            "graph": ["Graphs", "Graph Traversal"],
            "tree": ["Trees", "Binary Tree", "BST"],
            "sort": ["Sorting"],
            "search": ["Searching", "Binary Search"],
            "complex": ["Complexity Analysis"],
            "algorithm": ["Algorithms"],
            "recursion": ["Recursion"],
            "dynamic": ["Dynamic Programming"],
            "greedy": ["Greedy Algorithms"],
            "hash": ["Hash Tables"],
            "array": ["Arrays"],
            "stack": ["Stacks"],
            "queue": ["Queues"],
            "heap": ["Heap"],
            "linked": ["Linked Lists"]
        }
        
        question_lower = question_text.lower()
        topics = []
        
        for keyword, topic_list in keyword_mapping.items():
            if keyword in question_lower:
                topics.extend(topic_list)
        
        return list(set(topics))  # הסרת כפילויות
    
    def assign_topics_to_question(self, question: QuestionBank) -> None:
        """מקצה נושאים לשאלה ומשמר במסד הנתונים"""
        topics = self.extract_topics_from_question(question.question_text)
        
        for topic_name in topics:
            # צור נושא אם לא קיים
            topic, created = Topic.objects.get_or_create(
                name=topic_name,
                defaults={'description': f'Questions related to {topic_name}'}
            )
            
            # צור קישור בין שאלה לנושא
            QuestionTopic.objects.get_or_create(
                question=question,
                topic=topic,
                defaults={'confidence_score': 1.0}
            )
        
        logger.info(f"Assigned {len(topics)} topics to question {question.id}")
    
    def get_topics_for_question(self, question: QuestionBank) -> List[Topic]:
                """מחזיר את כל הנושאים של שאלה"""
            
                
                # Debug: Check what's in database
                qt_count = QuestionTopic.objects.filter(question=question).count()  # ADD THIS
                logger.info(f"  DB check: Question {question.id} has {qt_count} QuestionTopic records")  # ADD THIS
                
                return [qt.topic for qt in question.topics.all()]