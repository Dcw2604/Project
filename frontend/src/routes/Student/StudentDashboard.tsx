import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth'
import { useStudentExams, useDiscovery } from '@/lib/queries'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useToast } from '@/hooks/use-toast'
import { LogOut, BookOpen, AlertCircle, RefreshCw } from 'lucide-react'
import ExamCard from './ExamCard'
import ExamRunner from './ExamRunner'

export default function StudentDashboard() {
  const { user, logout } = useAuth()
  const { toast } = useToast()
  const [selectedExamId, setSelectedExamId] = useState<string | number | null>(null)
  
  const { data: exams, isLoading, error, refetch } = useStudentExams()
  const { data: discovery } = useDiscovery()

  // Check for examId in URL on mount
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const examId = urlParams.get('examId')
    if (examId) {
      setSelectedExamId(examId)
    }
  }, [])

  const handleStartExam = (examId: string | number) => {
    setSelectedExamId(examId)
  }

  const handleExamComplete = () => {
    setSelectedExamId(null)
    refetch()
    // Clean up URL
    const url = new URL(window.location.href)
    url.searchParams.delete('examId')
    window.history.replaceState({}, '', url.toString())
    toast({
      title: "Exam Completed",
      description: "You have completed the exam successfully",
    })
  }

  const handleLogout = () => {
    logout()
    toast({
      title: "Signed Out",
      description: "You have been signed out successfully",
    })
  }

  const handleRefresh = () => {
    refetch()
    toast({
      title: "Refreshed",
      description: "Exam list has been refreshed",
    })
  }

  // If an exam is selected, show the exam runner
  if (selectedExamId) {
    return (
      <ExamRunner 
        examId={selectedExamId}
        onComplete={handleExamComplete}
        onBack={() => setSelectedExamId(null)}
      />
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                Student Dashboard
              </h1>
              <p className="text-sm text-gray-500">
                Welcome back, {user?.name}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={handleRefresh} disabled={isLoading}>
                <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button variant="outline" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="space-y-6">
          {/* Discovery Status */}
          {discovery && (
            <Card>
              <CardContent className="pt-6">
                <div className="text-sm text-muted-foreground">
                {exams && exams.length > 0 
                  ? `${exams.filter(e => !e.completed).length} available, ${exams.filter(e => e.completed).length} completed`
                  : 'No exams available'}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="space-y-4">
              <Skeleton className="h-32 w-full" />
              <Skeleton className="h-32 w-full" />
              <Skeleton className="h-32 w-full" />
            </div>
          )}

          {/* Error State */}
          {error && (
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 text-red-600">
                  <AlertCircle className="h-5 w-5" />
                  <span>Failed to load exams: {error.message}</span>
                </div>
                <Button 
                  variant="outline" 
                  onClick={handleRefresh}
                  className="mt-4"
                >
                  Try Again
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Empty State */}
          {!isLoading && !error && (!exams || exams.length === 0) && (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-8">
                  <div className="mx-auto w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                    <BookOpen className="h-6 w-6 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    No Available Exams
                  </h3>
                  <p className="text-gray-500 mb-4">
                    {!discovery?.exams 
                      ? "No exams are currently available. Check back later or ask your teacher for an exam link."
                      : "No exams have been assigned to you yet."
                    }
                  </p>
                  <Button variant="outline" onClick={handleRefresh}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Exams List */}
          {!isLoading && !error && exams && exams.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">
                Available Exams ({exams.filter(e => !e.completed).length})
                </h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {exams
                .filter((exam) => !exam.completed)
                .map((exam) => (
                  <ExamCard
                    key={exam.id}
                    exam={exam}
                    onStart={handleStartExam}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}