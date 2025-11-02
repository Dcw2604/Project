// frontend/src/routes/Student/ExamRunner.tsx

import { useState, useEffect, useRef } from "react";
import { useAuth } from "@/lib/auth";
import { useExamRunner } from "@/lib/queries";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { 
  ArrowLeft, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Flag, 
  ChevronLeft, 
  ChevronRight,
  List,
  AlertCircle
} from "lucide-react";
import QuestionCard from "./QuestionCard";
import type {
  Question,
  SubmitAnswersResponse,
  StartExamResponse,
  FinishExamResponse,
} from "@/lib/types";

interface ExamRunnerProps {
  examId: string | number;
  onComplete: () => void;
  onBack: () => void;
}

interface ExamState {
  sessionId: number | null;
  currentQuestionIndex: number;
  answers: Record<number, string>;
  questions: Question[];
  isFinished: boolean;
  score: number | null;
  totalQuestions: number | null;
  answeredQuestions: Set<number>;
}

export default function ExamRunner({
  examId,
  onComplete,
  onBack,
}: ExamRunnerProps) {
  const { user } = useAuth();
  const { toast } = useToast();
  const { startExam, questions, submitAnswers, finishExam, isLoading, error } =
    useExamRunner(examId);

  const [examState, setExamState] = useState<ExamState>({
    sessionId: null,
    currentQuestionIndex: 0,
    answers: {},
    questions: [],
    isFinished: false,
    score: null,
    totalQuestions: null,
    answeredQuestions: new Set(),
  });

  const [timeRemaining, setTimeRemaining] = useState(60 * 60); // 60 minutes
  const [showNavigation, setShowNavigation] = useState(false);
  const [showReviewScreen, setShowReviewScreen] = useState(false);
  const hasStartedRef = useRef(false);

  // Load saved state from sessionStorage
  useEffect(() => {
    const savedState = sessionStorage.getItem(`exam_${examId}`);
    if (savedState) {
      try {
        const parsed = JSON.parse(savedState);
        // Convert answeredQuestions array back to Set
        if (parsed.answeredQuestions && Array.isArray(parsed.answeredQuestions)) {
          parsed.answeredQuestions = new Set(parsed.answeredQuestions);
        }
        setExamState((prev) => ({ ...prev, ...parsed }));
      } catch (error) {
        console.error("Failed to load saved Quiz state:", error);
      }
    }
  }, [examId]);

  // Save state to sessionStorage
  useEffect(() => {
    const stateToSave = {
      ...examState,
      answeredQuestions: Array.from(examState.answeredQuestions),
    };
    sessionStorage.setItem(`exam_${examId}`, JSON.stringify(stateToSave));
  }, [examId, examState]);

  // Timer countdown
  useEffect(() => {
    if (examState.isFinished || timeRemaining <= 0) return;

    const timer = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          handleFinishExam();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [examState.isFinished, timeRemaining]);

  // Start exam when component mounts
  useEffect(() => {
    if (
      !examState.sessionId &&
      !isLoading &&
      user?.id &&
      !hasStartedRef.current
    ) {
      hasStartedRef.current = true;
      handleStartExam();
    }
  }, [examState.sessionId, isLoading, user?.id]);

  const handleStartExam = async () => {
    if (!user) return;

    try {
      const result = (await startExam.mutateAsync({
        examId,
        studentId: user.id || 0,
      })) as StartExamResponse;

      if (result.success) {
        setExamState((prev) => ({
          ...prev,
          sessionId: result.session_id,
          questions: result.selected_questions || [],
          totalQuestions: result.total_questions || null,
        }));
      }
    } catch (error) {
      console.error("Start Quiz error:", error);
      hasStartedRef.current = false;
      toast({
        title: "Failed to Start Quiz",
        description:
          error instanceof Error ? error.message : "Could not start Quiz",
        variant: "destructive",
      });
    }
  };

  const handleSubmitAnswer = async (answer: string) => {
    if (!examState.sessionId) return;

    try {
      const currentQuestion =
        examState.questions[examState.currentQuestionIndex];
      const result = (await submitAnswers.mutateAsync({
        examId,
        payload: {
          exam_session_id: examState.sessionId,
          question_id: Number(currentQuestion.id),
          answer: answer,
        },
      })) as SubmitAnswersResponse;

      // Mark question as answered
      setExamState((prev) => ({
        ...prev,
        answeredQuestions: new Set(prev.answeredQuestions).add(prev.currentQuestionIndex),
        answers: {
          ...prev.answers,
          [prev.currentQuestionIndex]: answer,
        },
      }));

      // Show feedback
      if (result.is_correct) {
        toast({
          title: "✅ Correct!",
          description: `Score: ${result.score}/${result.max_score}`,
        });
      } else {
        toast({
          title: "❌ Incorrect",
          description: `Score: ${result.score}/${result.max_score}`,
          variant: "destructive",
        });
      }

      // Auto-advance to next question after a short delay
      setTimeout(() => {
        handleNextQuestion();
      }, 800);
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to submit answer",
        variant: "destructive",
      });
    }
  };

  const handleNextQuestion = () => {
    const nextIndex = examState.currentQuestionIndex + 1;
    const maxQuestions = examState.totalQuestions || 10;

    if (nextIndex < maxQuestions && nextIndex < examState.questions.length) {
      setExamState((prev) => ({
        ...prev,
        currentQuestionIndex: nextIndex,
      }));
    } else {
      // All questions answered, show review screen
      setShowReviewScreen(true);
    }
  };

  const handlePreviousQuestion = () => {
    if (examState.currentQuestionIndex > 0) {
      setExamState((prev) => ({
        ...prev,
        currentQuestionIndex: prev.currentQuestionIndex - 1,
      }));
    }
  };

  const handleJumpToQuestion = (index: number) => {
    setExamState((prev) => ({
      ...prev,
      currentQuestionIndex: index,
    }));
    setShowNavigation(false);
  };

  const handleFinishExam = async () => {
    if (!examState.sessionId) return;

    try {
      const result = (await finishExam.mutateAsync({
        examId,
        examSessionId: examState.sessionId,
      })) as FinishExamResponse;

      setExamState((prev) => ({
        ...prev,
        isFinished: true,
        score: result.correct_answers || 0,
        totalQuestions: result.total_questions_in_exam || 0,
      }));

      sessionStorage.removeItem(`exam_${examId}`);

      setTimeout(() => {
        onComplete();
      }, 2000);
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to finish Quiz",
        variant: "destructive",
      });
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const currentQuestion = examState.questions[examState.currentQuestionIndex];
  const progress =
    examState.totalQuestions && examState.totalQuestions > 0
      ? ((examState.currentQuestionIndex + 1) / examState.totalQuestions) * 100
      : 0;
  const answeredCount = examState.answeredQuestions.size;
  const totalCount = examState.totalQuestions || 10;

  // Review Screen
  if (showReviewScreen) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 py-12">
        <div className="max-w-3xl mx-auto px-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl flex items-center gap-2">
                <AlertCircle className="h-6 w-6 text-blue-600" />
                Review Your Answers
              </CardTitle>
              <CardDescription>
                Please review your answers before submitting the Quiz
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <p className="text-sm text-green-700 font-medium">Answered</p>
                  <p className="text-3xl font-bold text-green-900">{answeredCount}</p>
                </div>
                <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
                  <p className="text-sm text-orange-700 font-medium">Unanswered</p>
                  <p className="text-3xl font-bold text-orange-900">
                    {totalCount - answeredCount}
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                <h4 className="font-semibold">Question Status:</h4>
                <div className="grid grid-cols-5 gap-2">
                  {Array.from({ length: totalCount }).map((_, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        setShowReviewScreen(false);
                        handleJumpToQuestion(index);
                      }}
                      className={`p-3 rounded-lg text-sm font-medium transition-colors ${
                        examState.answeredQuestions.has(index)
                          ? "bg-green-100 text-green-800 border border-green-300 hover:bg-green-200"
                          : "bg-orange-100 text-orange-800 border border-orange-300 hover:bg-orange-200"
                      }`}
                    >
                      Q{index + 1}
                    </button>
                  ))}
                </div>
              </div>

              {answeredCount < totalCount && (
                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <p className="text-sm text-yellow-800">
                    ⚠️ You have {totalCount - answeredCount} unanswered question(s). 
                    Would you like to answer them before submitting?
                  </p>
                </div>
              )}

              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => setShowReviewScreen(false)}
                  className="flex-1"
                >
                  Continue Answering
                </Button>
                <Button
                  onClick={handleFinishExam}
                  disabled={finishExam.isPending}
                  className="flex-1 bg-green-600 hover:bg-green-700"
                >
                  {finishExam.isPending ? "Submitting..." : "Submit Quiz"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Loading state
  if (isLoading && !examState.sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-500 border-t-transparent mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Starting Quiz...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-orange-50">
        <Card className="max-w-md">
          <CardContent className="pt-6">
            <div className="text-center">
              <XCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Quiz Error
              </h3>
              <p className="text-gray-600 mb-4">
                {error.message || "Failed to load Quiz"}
              </p>
              <Button onClick={onBack} variant="outline">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Exam completed
  if (examState.isFinished) {
    const percentage = examState.totalQuestions 
      ? Math.round((examState.score! / examState.totalQuestions) * 100)
      : 0;
    
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-blue-50">
        <Card className="max-w-lg">
          <CardContent className="pt-8 pb-6">
            <div className="text-center">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="h-12 w-12 text-green-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                Exam Completed!
              </h3>
              <p className="text-gray-600 mb-6">
                Congratulations on completing the Quiz
              </p>
              
              {examState.score !== null && (
                <div className="space-y-4">
                  <div className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                    <div className="text-sm text-gray-600 mb-2">Your Score</div>
                    <div className="text-5xl font-bold text-blue-600 mb-2">
                      {examState.score}/{examState.totalQuestions}
                    </div>
                    <div className="text-2xl font-semibold text-gray-700">
                      {percentage}%
                    </div>
                  </div>
                  
                  <div className="text-lg">
                    {percentage >= 80
                      ? "🌟 Excellent work! Outstanding performance!"
                      : percentage >= 60
                      ? "✅ Good job! Keep up the great work!"
                      : "💪 Keep learning! You've got this!"}
                  </div>
                </div>
              )}
              
              <Button onClick={onComplete} className="mt-6 w-full" size="lg">
                Back to Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // No questions available
  if (!currentQuestion) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100">
        <Card className="max-w-md">
          <CardContent className="pt-6">
            <div className="text-center">
              <Flag className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No Questions Available
              </h3>
              <p className="text-gray-600 mb-4">
                This Quiz doesn't have any questions yet.
              </p>
              <Button onClick={onBack} variant="outline">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Enhanced Header */}
      <div className="bg-white shadow-md border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Button variant="ghost" onClick={onBack} className="gap-2">
              <ArrowLeft className="h-4 w-4" />
              Exit Quiz
            </Button>

            <div className="flex items-center gap-6">
              {/* Question Counter */}
              <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <span className="text-blue-600 text-lg font-bold">
                  {examState.currentQuestionIndex + 1}
                </span>
                <span>/</span>
                <span>{examState.totalQuestions || 10}</span>
              </div>

              {/* Timer */}
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${
                timeRemaining < 300 ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'
              }`}>
                <Clock className="h-4 w-4" />
                <span className="font-mono font-semibold">{formatTime(timeRemaining)}</span>
              </div>

              {/* Navigation Toggle */}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowNavigation(!showNavigation)}
                className="gap-2"
              >
                <List className="h-4 w-4" />
                Questions
              </Button>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="bg-gray-100 h-2">
          <div
            className="bg-gradient-to-r from-blue-500 to-indigo-600 h-full transition-all duration-300"
            style={{ width: `${answeredCount/ totalCount * 100}%` }}
          />
        </div>
      </div>

      {/* Question Navigation Sidebar */}
      {showNavigation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-40" onClick={() => setShowNavigation(false)}>
          <div 
            className="absolute right-0 top-16 bottom-0 w-80 bg-white shadow-xl p-6 overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-4">
              <h3 className="text-lg font-semibold mb-2">Question Navigator</h3>
              <p className="text-sm text-gray-600">
                {answeredCount} of {totalCount} answered
              </p>
            </div>
            <div className="grid grid-cols-4 gap-2">
              {Array.from({ length: totalCount }).map((_, index) => (
                <button
                  key={index}
                  onClick={() => handleJumpToQuestion(index)}
                  className={`aspect-square rounded-lg text-sm font-semibold transition-all ${
                    index === examState.currentQuestionIndex
                      ? "bg-blue-600 text-white ring-2 ring-blue-300"
                      : examState.answeredQuestions.has(index)
                      ? "bg-green-100 text-green-800 hover:bg-green-200"
                      : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                  }`}
                >
                  {index + 1}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="space-y-4">
          {/* Status Bar */}
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <Badge variant={examState.answeredQuestions.has(examState.currentQuestionIndex) ? "default" : "secondary"}>
                {examState.answeredQuestions.has(examState.currentQuestionIndex) ? "✓ Answered" : "Unanswered"}
              </Badge>
              <span className="text-gray-600">
                {answeredCount}/{totalCount} questions answered
              </span>
            </div>
            <Button
              variant="default"
              onClick={() => setShowReviewScreen(true)}
              className="gap-2"
            >
              <Flag className="h-4 w-4" />
              Review & Submit
            </Button>
          </div>

          {/* Question Card */}
          <QuestionCard
            question={currentQuestion}
            questionNumber={examState.currentQuestionIndex + 1}
            totalQuestions={examState.totalQuestions || 10}
            onSubmit={handleSubmitAnswer}
            isLoading={submitAnswers.isPending}
            currentAnswer={
              examState.answers[examState.currentQuestionIndex] || ""
            }
          />

          {/* Navigation Buttons */}
          <div className="flex justify-between items-center pt-4">
            <Button
              variant="outline"
              onClick={handlePreviousQuestion}
              disabled={examState.currentQuestionIndex === 0}
              className="gap-2"
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>
            
            <Button
              variant="outline"
              onClick={handleNextQuestion}
              disabled={examState.currentQuestionIndex >= totalCount - 1}
              className="gap-2"
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}