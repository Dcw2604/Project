import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth'
import { useExamRunner } from '@/lib/queries'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { useToast } from '@/hooks/use-toast'
import { ArrowLeft, Clock, CheckCircle, XCircle, Flag } from 'lucide-react'
import QuestionCard from './QuestionCard'
import type { Question } from '@/lib/types'

interface ExamRunnerProps {
  examId: string | number
  onComplete: () => void
  onBack: () => void
}

interface ExamState {
  sessionId: number | null
  currentQuestionIndex: number
  answers: Record<number, string>
  attemptsUsed: Record<number, number>
  questions: Question[]
  isFinished: boolean
  score: number | null
  totalQuestions: number | null  // Add this line
  showHint: boolean
  hint: string
}

export default function ExamRunner({ examId, onComplete, onBack }: ExamRunnerProps) {
  const { user } = useAuth()
  const { toast } = useToast()
  const { startExam, questions, submitAnswers, finishExam, isLoading, error } = useExamRunner(examId)
  
  const [examState, setExamState] = useState<ExamState>({
    sessionId: null,
    currentQuestionIndex: 0,
    answers: {},
    attemptsUsed: {},
    questions: [],
    isFinished: false,
    score: null,
    totalQuestions: null,
    showHint: false,
    hint: ''
  })

  const [timeRemaining, setTimeRemaining] = useState(30 * 60) // 30 minutes in seconds

  // Load saved state from sessionStorage
  useEffect(() => {
    const savedState = sessionStorage.getItem(`exam_${examId}`)
    if (savedState) {
      try {
        const parsed = JSON.parse(savedState)
        setExamState(prev => ({ ...prev, ...parsed }))
      } catch (error) {
        console.error('Failed to load saved exam state:', error)
      }
    }
  }, [examId])

  // Save state to sessionStorage
  useEffect(() => {
    sessionStorage.setItem(`exam_${examId}`, JSON.stringify(examState))
  }, [examId, examState])

  // Timer countdown
  useEffect(() => {
    if (examState.isFinished || timeRemaining <= 0) return

    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          handleFinishExam()
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [examState.isFinished, timeRemaining])

  // Start exam when component mounts
  useEffect(() => {
    if (!examState.sessionId && !isLoading && user) {
      handleStartExam()
    }
  }, [examState.sessionId, isLoading, user])

  // Update questions when data is loaded
  useEffect(() => {
    if (questions.data?.questions) {
      setExamState(prev => ({
        ...prev,
        questions: questions.data.questions,
      }))
    }
  }, [questions.data])

  const handleStartExam = async () => {
    if (!user) return

    try {
      const result = await startExam.mutateAsync({
        examId,
        studentId: 6  // Fallback ID
      })

      if (result.success) {
        setExamState(prev => ({
          ...prev,
          sessionId: result.exam_session_id,
        }))
      }
    } catch (error) {
      console.error('Start exam error:', error)
      toast({
        title: "Failed to Start Exam",
        description: error instanceof Error ? error.message : 'Could not start exam',
        variant: "destructive",
      })
    }
  }

  const handleSubmitAnswer = async (answer: string) => {
    if (!examState.sessionId) return

    try {
      const currentQuestion = examState.questions[examState.currentQuestionIndex]
      const result = await submitAnswers.mutateAsync({
        examId,
        payload: {
          exam_session_id: examState.sessionId,
          question_id: Number(currentQuestion.id), // Convert to number
          answer: answer
        }
      })

      // Update answers
      setExamState(prev => ({
        ...prev,
        answers: {
          ...prev.answers,
          [examState.currentQuestionIndex]: answer
        }
      }))

      if (result.is_correct) {
        toast({
          title: "Correct!",
          description: result.reasoning || "Well done!",
        })
        
        // Move to next question
        setExamState(prev => ({
          ...prev,
          currentQuestionIndex: prev.currentQuestionIndex + 1,
          showHint: false,
          hint: ''
        }))
      } else {
        // Use backend's attempt tracking instead of manual increment
        console.log('Backend response:', result)
        console.log('attempts_used:', result.attempts_used)
        console.log('attempts_remaining:', result.attempts_remaining)
        console.log('should_advance:', result.should_advance)
        
        setExamState(prev => ({
          ...prev,
          attemptsUsed: {
            ...prev.attemptsUsed,
            [examState.currentQuestionIndex]: result.attempts_used || 0
          },
          showHint: true,
          hint: result.hint || "Try again!"
        }))

        toast({
          title: "Incorrect",
          description: result.hint || "Try again!",
          variant: "destructive",
        })

        // Move to next question if should advance (either correct or max attempts reached)
        if (result.should_advance) {
          console.log('Advancing to next question due to should_advance:', result.should_advance)
          setExamState(prev => ({
            ...prev,
            currentQuestionIndex: prev.currentQuestionIndex + 1,
            showHint: false,
            hint: ''
          }))
        }
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : 'Failed to submit answer',
        variant: "destructive",
      })
    }
  }

  const handleFinishExam = async () => {
    if (!examState.sessionId) return

    try {
      const result = await finishExam.mutateAsync({
        examId,
        examSessionId: examState.sessionId
      })

      setExamState(prev => ({
        ...prev,
        isFinished: true,
        score: result.correct_answers || 0,
        totalQuestions: result.total_questions_in_exam || 0
      }))

      // Clear session storage
      sessionStorage.removeItem(`exam_${examId}`)
      
      // Show completion after a delay
      setTimeout(() => {
        onComplete()
      }, 2000)
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : 'Failed to finish exam',
        variant: "destructive",
      })
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const currentQuestion = examState.questions[examState.currentQuestionIndex]
  const progress = examState.questions.length > 0 
    ? ((examState.currentQuestionIndex + 1) / examState.questions.length) * 100 
    : 0

  // Loading state
  if (isLoading && !examState.sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Starting exam...</p>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6">
            <div className="text-center">
              <XCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Exam Error
              </h3>
              <p className="text-gray-600 mb-4">
                {error.message || 'Failed to load exam'}
              </p>
              <Button onClick={onBack}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Exam completed
  if (examState.isFinished) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6">
            <div className="text-center">
              <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Exam Completed!
              </h3>
              <p className="text-gray-600 mb-4">
                {examState.score !== null ? `Score: ${examState.score} out of ${examState.totalQuestions || '?'} questions` : 'Thank you for completing the exam'}
              </p>
              <Button onClick={onComplete}>
                Back to Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // No questions available
  if (!currentQuestion) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6">
            <div className="text-center">
              <Flag className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No Questions Available
              </h3>
              <p className="text-gray-600 mb-4">
                This exam doesn't have any questions yet.
              </p>
              <Button onClick={onBack}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Button variant="outline" onClick={onBack}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
            
            <div className="flex items-center gap-4">
              <Button 
                variant="destructive" 
                onClick={handleFinishExam}
                disabled={finishExam.isPending}
              >
                {finishExam.isPending ? 'Finishing...' : 'Finish Exam'}
              </Button>
              
              <div className="text-sm text-gray-600">
                Question {examState.currentQuestionIndex + 1} of {examState.questions.length}
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Clock className="h-4 w-4" />
                {formatTime(timeRemaining)}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-gray-600">
              <span>Progress</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
        </div>
      </div>

      {/* Question */}
      <main className="max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <QuestionCard
          question={currentQuestion}
          questionNumber={examState.currentQuestionIndex + 1}
          totalQuestions={examState.questions.length}
          onSubmit={handleSubmitAnswer}
          isLoading={submitAnswers.isPending}
          currentAnswer={examState.answers[examState.currentQuestionIndex] || ''}
          attemptsUsed={examState.attemptsUsed[examState.currentQuestionIndex] || 0}
          attemptsRemaining={3 - (examState.attemptsUsed[examState.currentQuestionIndex] || 0)}
          showHint={examState.showHint}
          hint={examState.hint}
        />
      </main>
    </div>
  )
}