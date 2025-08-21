/**
 * 🎯 Task 3.2: ExamAnswerSubmission Component
 * 
 * React component for submitting answers during an active exam session
 * with automatic question progression and completion handling.
 */

import React, { useState, useEffect } from 'react';
import { useApi } from '../hooks/useApi';

const ExamAnswerSubmission = ({ examSessionId, onExamComplete }) => {
    const [currentQuestion, setCurrentQuestion] = useState(null);
    const [answer, setAnswer] = useState('');
    const [progress, setProgress] = useState(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [examCompleted, setExamCompleted] = useState(false);
    const [error, setError] = useState('');
    
    const { apiCall } = useApi();

    // Load initial exam progress
    useEffect(() => {
        loadExamProgress();
    }, [examSessionId]);

    const loadExamProgress = async () => {
        try {
            const response = await apiCall(`/exam-progress/${examSessionId}/`, 'GET');
            
            if (response.status === 'success') {
                setProgress(response.progress);
                setCurrentQuestion(response.progress.current_question);
                setExamCompleted(response.progress.is_completed);
                
                if (response.progress.is_completed) {
                    onExamComplete && onExamComplete(response.progress);
                }
            }
        } catch (err) {
            setError('Failed to load exam progress');
            console.error('Error loading exam progress:', err);
        }
    };

    const submitAnswer = async () => {
        if (!answer.trim()) {
            setError('Please provide an answer');
            return;
        }

        setIsSubmitting(true);
        setError('');

        try {
            const payload = {
                exam_session_id: examSessionId,
                question_id: currentQuestion.id,
                answer_text: answer.trim(),
                interaction_log: {
                    question_type: currentQuestion.question_type,
                    submitted_at: new Date().toISOString(),
                    answer_length: answer.trim().length
                }
            };

            const response = await apiCall('/student-answers/', 'POST', payload);

            if (response.status === 'saved') {
                // Move to next question
                setCurrentQuestion(response.next_question);
                setProgress(prev => ({
                    ...prev,
                    answered_questions: response.answered_questions,
                    progress_percentage: response.progress_percentage
                }));
                setAnswer(''); // Clear answer field
                
            } else if (response.status === 'completed') {
                // Exam completed
                setExamCompleted(true);
                setCurrentQuestion(null);
                setProgress(prev => ({
                    ...prev,
                    answered_questions: response.answered_questions,
                    is_completed: true,
                    final_score: response.final_score
                }));
                
                onExamComplete && onExamComplete(response);
            }

        } catch (err) {
            setError(err.message || 'Failed to submit answer');
            console.error('Error submitting answer:', err);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleAnswerChange = (e) => {
        setAnswer(e.target.value);
        setError('');
    };

    const handleMultipleChoiceAnswer = (option) => {
        setAnswer(option);
        setError('');
    };

    if (examCompleted) {
        return (
            <div className="exam-completed bg-green-50 border border-green-200 rounded-lg p-6">
                <div className="text-center">
                    <h2 className="text-2xl font-bold text-green-800 mb-4">
                        🎉 Exam Completed!
                    </h2>
                    
                    {progress && progress.final_score && (
                        <div className="bg-white rounded-lg p-4 mb-4">
                            <h3 className="text-lg font-semibold mb-2">Final Score</h3>
                            <div className="text-3xl font-bold text-blue-600">
                                {progress.final_score.correct_answers} / {progress.final_score.total_questions}
                            </div>
                            <div className="text-gray-600">
                                {Math.round((progress.final_score.correct_answers / progress.final_score.total_questions) * 100)}% Correct
                            </div>
                        </div>
                    )}
                    
                    <p className="text-gray-700">
                        Thank you for completing the exam. Your answers have been submitted successfully.
                    </p>
                </div>
            </div>
        );
    }

    if (!currentQuestion) {
        return (
            <div className="loading-state bg-gray-50 border border-gray-200 rounded-lg p-6">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading exam question...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="exam-answer-submission bg-white border border-gray-200 rounded-lg p-6">
            {/* Progress Bar */}
            {progress && (
                <div className="progress-section mb-6">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium text-gray-700">
                            Progress: {progress.answered_questions} / {progress.total_questions}
                        </span>
                        <span className="text-sm text-gray-500">
                            {progress.progress_percentage}% Complete
                        </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                            style={{ width: `${progress.progress_percentage}%` }}
                        ></div>
                    </div>
                </div>
            )}

            {/* Question Display */}
            <div className="question-section mb-6">
                <div className="flex items-start gap-3 mb-4">
                    <span className="bg-blue-100 text-blue-800 text-sm font-medium px-2.5 py-0.5 rounded">
                        Question {currentQuestion.order_index + 1}
                    </span>
                    <span className="bg-gray-100 text-gray-800 text-sm font-medium px-2.5 py-0.5 rounded">
                        {currentQuestion.question_type === 'multiple_choice' ? 'Multiple Choice' : 'Open Ended'}
                    </span>
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    {currentQuestion.question_text}
                </h3>

                {/* Answer Input */}
                {currentQuestion.question_type === 'multiple_choice' ? (
                    <div className="multiple-choice-options space-y-3">
                        {['A', 'B', 'C', 'D'].map(option => {
                            const optionText = currentQuestion[`option_${option.toLowerCase()}`];
                            if (!optionText) return null;
                            
                            return (
                                <label 
                                    key={option}
                                    className={`flex items-center p-3 border rounded-lg cursor-pointer transition-colors ${
                                        answer === option 
                                            ? 'border-blue-500 bg-blue-50' 
                                            : 'border-gray-200 hover:border-gray-300'
                                    }`}
                                >
                                    <input
                                        type="radio"
                                        name="answer"
                                        value={option}
                                        checked={answer === option}
                                        onChange={() => handleMultipleChoiceAnswer(option)}
                                        className="sr-only"
                                    />
                                    <div className={`w-4 h-4 rounded-full border-2 mr-3 ${
                                        answer === option ? 'border-blue-500 bg-blue-500' : 'border-gray-300'
                                    }`}>
                                        {answer === option && (
                                            <div className="w-2 h-2 bg-white rounded-full mx-auto mt-0.5"></div>
                                        )}
                                    </div>
                                    <span className="font-medium mr-2">{option}.</span>
                                    <span>{optionText}</span>
                                </label>
                            );
                        })}
                    </div>
                ) : (
                    <textarea
                        value={answer}
                        onChange={handleAnswerChange}
                        placeholder="Type your answer here..."
                        className="w-full h-32 p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        rows={4}
                    />
                )}
            </div>

            {/* Error Display */}
            {error && (
                <div className="error-message bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                    <p className="text-red-700 text-sm">{error}</p>
                </div>
            )}

            {/* Submit Button */}
            <div className="submit-section">
                <button
                    onClick={submitAnswer}
                    disabled={isSubmitting || !answer.trim()}
                    className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                        isSubmitting || !answer.trim()
                            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                >
                    {isSubmitting ? (
                        <div className="flex items-center justify-center">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                            Submitting...
                        </div>
                    ) : (
                        'Submit Answer & Continue'
                    )}
                </button>
            </div>
        </div>
    );
};

export default ExamAnswerSubmission;
