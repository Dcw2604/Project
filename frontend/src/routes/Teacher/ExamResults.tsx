import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { BarChart3, Users, Clock, TrendingUp, RefreshCw } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

interface ExamResult {
  student_name: string
  student_id: number
  exam_session_id: number
  score: number
  total_questions: number
  questions_answered: number
  completed_at: string | null
  started_at: string
}

interface StudentAnalytics {
  student_name: string
  exam_session_id: number
  overall_percentage: number
  total_questions: number
  total_correct: number
  topic_breakdown: {
    topic_name: string
    percentage: number
    questions_answered: number
    correct_answers: number
    performance_level: string
  }[]
  strengths: string[]
  weaknesses: string[]
}

interface Exam {
  id: number
  title: string
  document_title: string
  total_questions: number
  created_at: string
}

export default function ExamResults() {
  const [exams, setExams] = useState<Exam[]>([])
  const [selectedExamId, setSelectedExamId] = useState('')
  const [results, setResults] = useState<ExamResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingExams, setIsLoadingExams] = useState(true)
  const [expandedStudent, setExpandedStudent] = useState<number | null>(null)
  const [studentAnalytics, setStudentAnalytics] = useState<StudentAnalytics | null>(null)
  const [isLoadingAnalytics, setIsLoadingAnalytics] = useState(false)
  const [allStudentAnalytics, setAllStudentAnalytics] = useState<StudentAnalytics[]>([])
  const { toast } = useToast()

  // Fetch exams on component mount
  useEffect(() => {
    fetchExams()
  }, [])

  const fetchExams = async () => {
    setIsLoadingExams(true)
    try {
      const response = await fetch('http://127.0.0.1:8000/api/exams/')
      const data = await response.json()
      
      if (data.success) {
        setExams(data.exams)
      } else {
        toast({
          title: "Error",
          description: "Failed to fetch exams",
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch exams",
        variant: "destructive",
      })
    } finally {
      setIsLoadingExams(false)
    }
  }


  const fetchStudentAnalytics = async (studentId: number, examSessionId: number) => {
    setIsLoadingAnalytics(true)
    try {
      const response = await fetch(`/api/analytics/student/${studentId}/exam/${examSessionId}/`)
      const data = await response.json()
      
      setStudentAnalytics(data)
      setExpandedStudent(studentId)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch student analytics",
        variant: "destructive",
      })
    } finally {
      setIsLoadingAnalytics(false)
    }
  }
  
  const handleToggleStudent = (studentId: number, examSessionId: number) => {
    if (expandedStudent === studentId) {
      setExpandedStudent(null)
      setStudentAnalytics(null)
    } else {
      fetchStudentAnalytics(studentId, examSessionId)
    }
  }
  
  const fetchResults = async () => {
    if (!selectedExamId) {
      toast({
        title: "Error",
        description: "Please select an exam",
        variant: "destructive",
      })
      return
    }
  
    setIsLoading(true)
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/exams/${selectedExamId}/results/`)
      const data = await response.json()
      
      if (data.success) {
        // Store the results with placeholder data
        const analyticsArray: StudentAnalytics[] = []
        const resultsWithAnalytics = await Promise.all(
          data.results.map(async (result: ExamResult) => {
            // Fetch analytics for each student
            try {
              const analyticsResponse = await fetch(`/api/analytics/student/${result.student_id}/exam/${result.exam_session_id}/`)
              if (analyticsResponse.ok) {
                const analytics = await analyticsResponse.json()
                analyticsArray.push(analytics)
                // Merge analytics data into result
                return {
                  ...result,
                  score: analytics.total_correct,
                  total_questions: analytics.total_questions,
                  questions_answered: analytics.total_questions,
                  overall_percentage: analytics.overall_percentage,
                  started_at: result.started_at,
                  completed_at: result.completed_at,
                }
              }
            } catch (err) {
              console.log('Analytics not available for student', result.student_id)
            }
            // Return original if analytics fail
            return result
          })
        )
        
        setAllStudentAnalytics(analyticsArray)
        setResults(resultsWithAnalytics)
        toast({
          title: "Success",
          description: `Found ${data.results.length} student results`,
        })
      } else {
        toast({
          title: "Error",
          description: "Failed to fetch results",
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch results",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const calculateStats = () => {
    if (results.length === 0) return { avgScore: 0, totalStudents: 0, avgTime: 0 }
    
    const totalScore = results.reduce((sum, result) => sum + result.score, 0)
    const avgScore = Math.round((totalScore / results.length) * 10) / 10
    
    const totalTime = results.reduce((sum, result) => {
      if (result.completed_at) {
        const start = new Date(result.started_at)
        const end = new Date(result.completed_at)
        return sum + (end.getTime() - start.getTime()) / 1000 // seconds
      }
      return sum
    }, 0)
    const avgTimeSeconds = totalTime / results.filter(r => r.completed_at && r.started_at).length
    const avgTime = avgTimeSeconds >= 60 
      ? `${Math.round(avgTimeSeconds / 60)} min` 
      : `${Math.round(avgTimeSeconds)}s`
    
    return {
      avgScore,
      totalStudents: results.length,
      avgTime
    }
  }

  const calculateWeaknessData = () => {
    const weaknessCount: Record<string, number> = {}
    
    allStudentAnalytics.forEach(analytics => {
      analytics.weaknesses.forEach(weakness => {
        weaknessCount[weakness] = (weaknessCount[weakness] || 0) + 1
      })
    })
    
    // Convert to array format for pie chart
    const chartData = Object.entries(weaknessCount)
      .map(([name, value]) => ({
        name,
        value,
        percentage: Math.round((value / allStudentAnalytics.length) * 100)
      }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 6)  // Top 6 weaknesses
    
    return chartData
  }
  
  const COLORS = ['#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16', '#22c55e']

  const stats = calculateStats()
  const selectedExam = exams.find(exam => exam.id.toString() === selectedExamId)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Exam Results
        </CardTitle>
        <CardDescription>
          View student performance and exam analytics
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Exam Selection */}
          <div className="space-y-2">
            <Label htmlFor="examSelect">Select Exam</Label>
            <div className="flex gap-2">
              <Select value={selectedExamId} onValueChange={setSelectedExamId}>
                <SelectTrigger className="flex-1">
                  <SelectValue placeholder={isLoadingExams ? "Loading exams..." : "Choose an exam"} />
                </SelectTrigger>
                <SelectContent>
                  {exams.map((exam) => (
                    <SelectItem key={exam.id} value={exam.id.toString()}>
                      <div className="flex flex-col">
                        <span className="font-medium">{exam.title}</span>
                        <span className="text-sm text-gray-500">
                          {exam.document_title} • {exam.total_questions} questions
                        </span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button onClick={fetchResults} disabled={isLoading || !selectedExamId}>
                {isLoading ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <BarChart3 className="h-4 w-4" />
                )}
                {isLoading ? 'Loading...' : 'View Results'}
              </Button>
            </div>
          </div>

          {/* Selected Exam Info */}
          {selectedExam && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
              <h4 className="font-medium text-blue-900 mb-2">Selected Exam</h4>
              <div className="text-sm text-blue-800">
                <p><strong>Title:</strong> {selectedExam.title}</p>
                <p><strong>Document:</strong> {selectedExam.document_title}</p>
                <p><strong>Questions:</strong> {selectedExam.total_questions}</p>
                <p><strong>Created:</strong> {new Date(selectedExam.created_at).toLocaleDateString()}</p>
              </div>
            </div>
          )}

          {/* Areas for Improvement Pie Chart */}
          {results.length > 0 && allStudentAnalytics.length > 0 && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Areas for Improvement (All Students)
                </CardTitle>
                <CardDescription>
                  Most common weaknesses across {allStudentAnalytics.length} students
                </CardDescription>
              </CardHeader>
              <CardContent>
                {calculateWeaknessData().length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={calculateWeaknessData()}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percentage }) => `${name}: ${percentage}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {calculateWeaknessData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip 
                        formatter={(value: number) => [`${value} students`, 'Count']}
                      />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-center text-gray-500 py-8">
                    No weakness data available yet
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          {/* Results Table */}
          {results.length > 0 ? (
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Student Results</h3>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse border border-gray-200">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="border border-gray-200 px-4 py-2 text-left">Student</th>
                      <th className="border border-gray-200 px-4 py-2 text-left">Score</th>
                      <th className="border border-gray-200 px-4 py-2 text-left">Questions Answered</th>
                      <th className="border border-gray-200 px-4 py-2 text-left">Time Taken</th>
                      <th className="border border-gray-200 px-4 py-2 text-left">Status</th>
                      <th className="border border-gray-200 px-4 py-2 text-left">Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((result, index) => (
                      <React.Fragment key={`student-${result.student_id}-${result.exam_session_id}`}>
                        {/* Main Row */}
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="border border-gray-200 px-4 py-2">
                            <div>
                              <div className="font-medium">{result.student_name}</div>
                              <div className="text-sm text-gray-500">ID: {result.student_id}</div>
                            </div>
                          </td>
                          <td className="border border-gray-200 px-4 py-2">
                            <Badge variant={result.score >= result.total_questions * 0.7 ? "default" : "destructive"}>
                              {result.score}/{result.total_questions}
                            </Badge>
                            <div className="text-sm text-gray-500 mt-1">
                              {Math.round((result.score / result.total_questions) * 100)}%
                            </div>
                          </td>
                          <td className="border border-gray-200 px-4 py-2">
                            {result.questions_answered}
                          </td>
                          <td className="border border-gray-200 px-4 py-2">
                            {result.completed_at && result.started_at ? (
                              (() => {
                                const milliseconds = new Date(result.completed_at).getTime() - new Date(result.started_at).getTime()
                                const totalSeconds = Math.round(milliseconds / 1000)
                                const minutes = Math.floor(totalSeconds / 60)
                                const seconds = totalSeconds % 60
                                
                                if (minutes > 0) {
                                  return <span className="text-sm">{minutes} min {seconds}s</span>
                                } else {
                                  return <span className="text-sm">{seconds}s</span>
                                }
                              })()
                            ) : (
                              <span className="text-sm text-gray-400">-</span>
                            )}
                          </td>
                          <td className="border border-gray-200 px-4 py-2">
                            {result.completed_at ? (
                              <Badge variant="default">Completed</Badge>
                            ) : (
                              <Badge variant="secondary">In Progress</Badge>
                            )}
                          </td>
                          <td className="border border-gray-200 px-4 py-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleToggleStudent(result.student_id, result.exam_session_id)}
                              disabled={isLoadingAnalytics && expandedStudent !== result.student_id}
                            >
                              {expandedStudent === result.student_id ? 'Hide Details' : 'View Details'}
                            </Button>
                          </td>
                        </tr>

                        {/* Expanded Analytics Row */}
                        {expandedStudent === result.student_id && studentAnalytics && (
                          <tr>
                            <td colSpan={6} className="border border-gray-200 bg-gray-50 p-6">
                              {isLoadingAnalytics ? (
                                <div className="text-center py-4">Loading analytics...</div>
                              ) : (
                                <div className="space-y-6">
                                  {/* Overall Performance */}
                                  <div>
                                    <h4 className="font-semibold mb-2">Overall Performance</h4>
                                    <div className="grid grid-cols-3 gap-4">
                                      <div className="p-3 bg-white rounded border">
                                        <div className="text-sm text-gray-600">Correct Answers</div>
                                        <div className="text-lg font-bold">{studentAnalytics.total_correct}/{studentAnalytics.total_questions}</div>
                                      </div>
                                      <div className="p-3 bg-white rounded border">
                                        <div className="text-sm text-gray-600">Overall Score</div>
                                        <div className="text-lg font-bold">{Math.round(studentAnalytics.overall_percentage)}%</div>
                                      </div>
                                      <div className="p-3 bg-white rounded border">
                                        <div className="text-sm text-gray-600">Performance Level</div>
                                        <div className="text-lg font-bold">
                                          {studentAnalytics.overall_percentage >= 80 ? '🌟 Excellent' : 
                                          studentAnalytics.overall_percentage >= 60 ? '✅ Good' : 
                                          studentAnalytics.overall_percentage >= 40 ? '⚠️ Fair' : '❌ Needs Help'}
                                        </div>
                                      </div>
                                    </div>
                                  </div>

                                  {/* Strengths */}
                                  {studentAnalytics.strengths && studentAnalytics.strengths.length > 0 && (
                                    <div>
                                      <h4 className="font-semibold mb-2 text-green-700">💪 Strengths</h4>
                                      <div className="flex flex-wrap gap-2">
                                        {studentAnalytics.strengths.map((topic, i) => (
                                          <Badge key={i} variant="default" className="bg-green-100 text-green-800 border-green-300">
                                            {topic}
                                          </Badge>
                                        ))}
                                      </div>
                                    </div>
                                  )}

                                  {/* Weaknesses */}
                                  {studentAnalytics.weaknesses && studentAnalytics.weaknesses.length > 0 && (
                                    <div>
                                      <h4 className="font-semibold mb-2 text-red-700">📚 Areas for Improvement</h4>
                                      <div className="flex flex-wrap gap-2">
                                        {studentAnalytics.weaknesses.map((topic, i) => (
                                          <Badge key={i} variant="destructive" className="bg-red-100 text-red-800 border-red-300">
                                            {topic}
                                          </Badge>
                                        ))}
                                      </div>
                                    </div>
                                  )}

                                  {/* Topic Breakdown */}
                                  <div>
                                    <h4 className="font-semibold mb-3">📊 Performance by Topic</h4>
                                    <div className="overflow-x-auto">
                                      <table className="w-full text-sm border border-gray-200">
                                        <thead>
                                          <tr className="bg-white">
                                            <th className="border border-gray-200 px-3 py-2 text-left">Topic</th>
                                            <th className="border border-gray-200 px-3 py-2 text-center">Score</th>
                                            <th className="border border-gray-200 px-3 py-2 text-center">Percentage</th>
                                            <th className="border border-gray-200 px-3 py-2 text-left">Level</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {studentAnalytics.topic_breakdown.map((topic, i) => (
                                            <tr key={i} className="hover:bg-white">
                                              <td className="border border-gray-200 px-3 py-2">{topic.topic_name}</td>
                                              <td className="border border-gray-200 px-3 py-2 text-center">
                                                {topic.correct_answers}/{topic.questions_answered}
                                              </td>
                                              <td className="border border-gray-200 px-3 py-2 text-center">
                                                <span className={
                                                  topic.percentage >= 80 ? 'text-green-600 font-semibold' :
                                                  topic.percentage >= 60 ? 'text-blue-600' :
                                                  topic.percentage >= 40 ? 'text-yellow-600' :
                                                  'text-red-600 font-semibold'
                                                }>
                                                  {Math.round(topic.percentage)}%
                                                </span>
                                              </td>
                                              <td className="border border-gray-200 px-3 py-2">
                                                <Badge 
                                                  variant={
                                                    topic.performance_level === "Excellent" ? "default" :
                                                    topic.performance_level === "Good" ? "secondary" :
                                                    "destructive"
                                                  }
                                                  className="text-xs"
                                                >
                                                  {topic.performance_level}
                                                </Badge>
                                              </td>
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                    </div>
                                  </div>
                                </div>
                              )}
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            
          ) : selectedExamId ? (
            <div className="text-center py-8">
              <div className="mx-auto w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <BarChart3 className="h-6 w-6 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No Results Found
              </h3>
              <p className="text-gray-500">
                No students have taken this exam yet.
              </p>
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="mx-auto w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <BarChart3 className="h-6 w-6 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Select an Exam
              </h3>
              <p className="text-gray-500">
                Choose an exam from the dropdown to view student results.
              </p>
            </div>
          )}
          {/* Statistics */}
          {results.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Users className="h-4 w-4" />
                  <span className="text-sm font-medium">Total Students</span>
                </div>
                <div className="text-2xl font-bold">{stats.totalStudents}</div>
              </div>
              
              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Clock className="h-4 w-4" />
                  <span className="text-sm font-medium">Avg. Time (min)</span>
                </div>
                <div className="text-2xl font-bold">{stats.avgTime}</div>
              </div>
              
              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="h-4 w-4" />
                  <span className="text-sm font-medium">Avg. Score</span>
                </div>
                <div className="text-2xl font-bold">{stats.avgScore}</div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}