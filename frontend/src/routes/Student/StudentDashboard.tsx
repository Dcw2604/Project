// frontend/src/routes/Student/StudentDashboard.tsx

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth'
import { useStudentExams, useDiscovery } from '@/lib/queries'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/use-toast'
import { 
  LogOut, 
  BookOpen, 
  AlertCircle, 
  RefreshCw,
  TrendingUp,
  Clock,
  CheckCircle2,
  Target,
  Search,
  GraduationCap,
  BarChart3
} from 'lucide-react'
import ExamCard from './ExamCard'
import ExamRunner from './ExamRunner'

interface StudentStats {
  totalExamsTaken: number
  totalExamsAvailable: number
  averageScore: number
  completionRate: number
  recentScores: number[]
}

export default function StudentDashboard() {
  const { user, logout } = useAuth()
  const { toast } = useToast()
  const [selectedExamId, setSelectedExamId] = useState<string | number | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [activeTab, setActiveTab] = useState('available')
  const [stats, setStats] = useState<StudentStats>({
    totalExamsTaken: 0,
    totalExamsAvailable: 0,
    averageScore: 0,
    completionRate: 0,
    recentScores: []
  })
  
  const { data: exams, isLoading, error, refetch } = useStudentExams()
  const { data: discovery } = useDiscovery()

  // Calculate stats when exams data changes
  useEffect(() => {
    if (exams) {
      const completed = exams.filter(e => e.completed)
      const available = exams.filter(e => !e.completed)
      const scores = completed.map(e => e.score || 0)
      const avgScore = scores.length > 0 
        ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length)
        : 0
      const completionRate = exams.length > 0
        ? Math.round((completed.length / exams.length) * 100)
        : 0

      setStats({
        totalExamsTaken: completed.length,
        totalExamsAvailable: available.length,
        averageScore: avgScore,
        completionRate,
        recentScores: scores.slice(-5).reverse()
      })
    }
  }, [exams])

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
    const url = new URL(window.location.href)
    url.searchParams.delete('examId')
    window.history.replaceState({}, '', url.toString())
    toast({
      title: "Quiz Completed! 🎉",
      description: "Great job! Your results have been saved.",
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
      description: "Quiz list has been updated",
    })
  }

  // Filter exams based on search query
  const filteredExams = exams?.filter(exam =>
    exam.title.toLowerCase().includes(searchQuery.toLowerCase())
  ) || []

  const availableExams = filteredExams.filter(e => !e.completed)
  const completedExams = filteredExams.filter(e => e.completed)

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
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Enhanced Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-blue-600 rounded-lg flex items-center justify-center">
                <GraduationCap className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Student Dashboard
                </h1>
                <p className="text-sm text-gray-500">
                  Welcome back, {user?.name}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleRefresh} 
                disabled={isLoading}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleLogout}
                className="hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition-colors"
              >
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
          {/* Quick Stats Cards */}
          {!isLoading && exams && exams.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Card className="border-l-4 border-l-blue-500 hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Available Quizzes</p>
                      <p className="text-3xl font-bold text-gray-900 mt-2">
                        {stats.totalExamsAvailable}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">Ready to take</p>
                    </div>
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <BookOpen className="h-6 w-6 text-blue-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-l-4 border-l-green-500 hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Completed</p>
                      <p className="text-3xl font-bold text-gray-900 mt-2">
                        {stats.totalExamsTaken}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">Quizzes taken</p>
                    </div>
                    <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                      <CheckCircle2 className="h-6 w-6 text-green-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>


              <Card className="border-l-4 border-l-orange-500 hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Completion Rate</p>
                      <p className="text-3xl font-bold text-gray-900 mt-2">
                        {stats.completionRate}%
                      </p>
                      <p className="text-xs text-gray-500 mt-1">Progress</p>
                    </div>
                    <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
                      <TrendingUp className="h-6 w-6 text-orange-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
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
                  <span>Failed to load Quizzes: {error.message}</span>
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
                <div className="text-center py-12">
                  <div className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center mb-4">
                    <BookOpen className="h-8 w-8 text-blue-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    No Quizzes Available
                  </h3>
                  <p className="text-gray-500 mb-6 max-w-md mx-auto">
                    {!discovery?.exams 
                      ? "No Quizzes are currently available. Check back later or contact your teacher."
                      : "No Quizzes have been assigned to you yet."
                    }
                  </p>
                  <Button variant="outline" onClick={handleRefresh}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Check for Updates
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Exams Section with Tabs */}
          {!isLoading && !error && exams && exams.length > 0 && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Your Quizzes</CardTitle>
                    <CardDescription>
                      {exams.length} total Quizzes{exams.length !== 1 ? 's' : ''}
                    </CardDescription>
                  </div>
                  {/* Search Bar */}
                  <div className="relative w-64">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search Quizzes..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-9"
                    />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <Tabs value={activeTab} onValueChange={setActiveTab}>
                  <TabsList className="grid w-full grid-cols-2 mb-6">
                    <TabsTrigger value="available" className="flex items-center gap-2">
                      <BookOpen className="h-4 w-4" />
                      Available ({availableExams.length})
                    </TabsTrigger>
                    <TabsTrigger value="completed" className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4" />
                      Completed ({completedExams.length})
                    </TabsTrigger>
                  </TabsList>

                  {/* Available Exams Tab */}
                  <TabsContent value="available" className="space-y-4">
                    {availableExams.length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {availableExams.map((exam) => (
                          <ExamCard
                            key={exam.id}
                            exam={exam}
                            onStart={handleStartExam}
                          />
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-12">
                        <BookOpen className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                        <p className="text-gray-500">
                          {searchQuery ? 'No Quizzes match your search' : 'No available Quizzes'}
                        </p>
                      </div>
                    )}
                  </TabsContent>

                  {/* Completed Exams Tab */}
                  <TabsContent value="completed" className="space-y-4">
                    {completedExams.length > 0 ? (
                      <div className="space-y-3">
                        {completedExams.map((exam) => (
                          <Card key={exam.id} className="hover:shadow-md transition-shadow">
                            <CardContent className="pt-6">
                              <div className="flex items-center justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center gap-3 mb-2">
                                    <h3 className="font-semibold text-lg">{exam.title}</h3>
                                    <Badge variant="secondary">
                                      <CheckCircle2 className="h-3 w-3 mr-1" />
                                      Completed
                                    </Badge>
                                  </div>
                                  <div className="flex items-center gap-4 text-sm text-gray-600">
                                    <span className="flex items-center gap-1">
                                      <Clock className="h-4 w-4" />
                                      {exam.completed_at 
                                        ? new Date(exam.completed_at).toLocaleDateString()
                                        : exam.created_at
                                        ? new Date(exam.created_at).toLocaleDateString()
                                        : 'Unknown date'}
                                    </span>
                                    {exam.total_questions && (
                                      <span>{exam.total_questions} questions</span>
                                    )}
                                  </div>
                                </div>
                                
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-12">
                        <CheckCircle2 className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                        <p className="text-gray-500">
                          {searchQuery ? 'No completed Quizzes match your search' : 'No completed Quizzes yet'}
                        </p>
                        {!searchQuery && availableExams.length > 0 && (
                          <Button
                            variant="outline"
                            className="mt-4"
                            onClick={() => setActiveTab('available')}
                          >
                            View Available Quizzes
                          </Button>
                        )}
                      </div>
                    )}
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  );
}