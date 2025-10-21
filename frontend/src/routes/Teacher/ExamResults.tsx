// frontend/src/routes/Teacher/ExamResults.tsx

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { BarChart3, Users, Clock, TrendingUp, RefreshCw, Download, Search, Filter, ArrowUpDown, AlertCircle } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'

interface ExamResult {
  student_name: string
  student_id: number
  exam_session_id: number
  score: number
  total_questions: number
  questions_answered: number
  completed_at: string | null
  started_at: string
  overall_percentage?: number
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

type SortField = 'name' | 'score' | 'time'
type SortOrder = 'asc' | 'desc'

export default function ExamResults() {
  const [exams, setExams] = useState<Exam[]>([])
  const [selectedExamId, setSelectedExamId] = useState('')
  const [results, setResults] = useState<ExamResult[]>([])
  const [filteredResults, setFilteredResults] = useState<ExamResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingExams, setIsLoadingExams] = useState(true)
  const [expandedStudent, setExpandedStudent] = useState<number | null>(null)
  const [studentAnalytics, setStudentAnalytics] = useState<StudentAnalytics | null>(null)
  const [isLoadingAnalytics, setIsLoadingAnalytics] = useState(false)
  const [allStudentAnalytics, setAllStudentAnalytics] = useState<StudentAnalytics[]>([])
  
  // Filter and Sort States
  const [searchQuery, setSearchQuery] = useState('')
  const [sortField, setSortField] = useState<SortField>('score')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')
  const [scoreFilter, setScoreFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all')
  
  const { toast } = useToast()

  useEffect(() => {
    fetchExams()
  }, [])

  useEffect(() => {
    applyFiltersAndSort()
  }, [results, searchQuery, sortField, sortOrder, scoreFilter])

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
        const analyticsArray: StudentAnalytics[] = []
        const resultsWithAnalytics = await Promise.all(
          data.results.map(async (result: ExamResult) => {
            try {
              const analyticsResponse = await fetch(`/api/analytics/student/${result.student_id}/exam/${result.exam_session_id}/`)
              if (analyticsResponse.ok) {
                const analytics = await analyticsResponse.json()
                analyticsArray.push(analytics)
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

  const applyFiltersAndSort = () => {
    let filtered = [...results]

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(result =>
        result.student_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        result.student_id.toString().includes(searchQuery)
      )
    }

    // Apply score filter
    if (scoreFilter !== 'all') {
      filtered = filtered.filter(result => {
        const percentage = (result.score / result.total_questions) * 100
        if (scoreFilter === 'high') return percentage >= 70
        if (scoreFilter === 'medium') return percentage >= 40 && percentage < 70
        if (scoreFilter === 'low') return percentage < 40
        return true
      })
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let comparison = 0
      
      if (sortField === 'name') {
        comparison = a.student_name.localeCompare(b.student_name)
      } else if (sortField === 'score') {
        const aPercentage = (a.score / a.total_questions) * 100
        const bPercentage = (b.score / b.total_questions) * 100
        comparison = aPercentage - bPercentage
      } else if (sortField === 'time') {
        if (a.completed_at && b.completed_at && a.started_at && b.started_at) {
          const aTime = new Date(a.completed_at).getTime() - new Date(a.started_at).getTime()
          const bTime = new Date(b.completed_at).getTime() - new Date(b.started_at).getTime()
          comparison = aTime - bTime
        }
      }
      
      return sortOrder === 'asc' ? comparison : -comparison
    })

    setFilteredResults(filtered)
  }

  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortOrder('desc')
    }
  }

  const exportToCSV = () => {
    if (filteredResults.length === 0) return

    const headers = ['Student Name', 'Student ID', 'Score', 'Total Questions', 'Percentage', 'Time Taken', 'Status']
    const rows = filteredResults.map(result => {
      const percentage = Math.round((result.score / result.total_questions) * 100)
      const timeTaken = result.completed_at && result.started_at
        ? `${Math.round((new Date(result.completed_at).getTime() - new Date(result.started_at).getTime()) / 60000)} min`
        : 'N/A'
      const status = result.completed_at ? 'Completed' : 'In Progress'
      
      return [
        result.student_name,
        result.student_id,
        result.score,
        result.total_questions,
        `${percentage}%`,
        timeTaken,
        status
      ]
    })

    const csvContent = [headers, ...rows]
      .map(row => row.map(cell => `"${cell}"`).join(','))
      .join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `exam-${selectedExamId}-results.csv`
    a.click()
    window.URL.revokeObjectURL(url)

    toast({
      title: "Exported",
      description: "Results exported to CSV successfully",
    })
  }

  const calculateStats = () => {
    if (filteredResults.length === 0) return { avgScore: 0, totalStudents: 0, avgTime: 0, passRate: 0 }
    
    const totalScore = filteredResults.reduce((sum, result) => sum + result.score, 0)
    const avgScore = Math.round((totalScore / filteredResults.length) * 10) / 10
    
    const totalTime = filteredResults.reduce((sum, result) => {
      if (result.completed_at) {
        const start = new Date(result.started_at)
        const end = new Date(result.completed_at)
        return sum + (end.getTime() - start.getTime()) / 1000
      }
      return sum
    }, 0)
    const avgTimeSeconds = totalTime / filteredResults.filter(r => r.completed_at && r.started_at).length
    const avgTime = avgTimeSeconds >= 60 
      ? `${Math.round(avgTimeSeconds / 60)} min` 
      : `${Math.round(avgTimeSeconds)}s`
    
    const passCount = filteredResults.filter(r => (r.score / r.total_questions) >= 0.6).length
    const passRate = Math.round((passCount / filteredResults.length) * 100)
    
    return {
      avgScore,
      totalStudents: filteredResults.length,
      avgTime,
      passRate
    }
  }

  const getScoreDistributionData = () => {
    const ranges = { 'Excellent (80-100%)': 0, 'Good (60-79%)': 0, 'Fair (40-59%)': 0, 'Poor (<40%)': 0 }
    
    filteredResults.forEach(result => {
      const percentage = (result.score / result.total_questions) * 100
      if (percentage >= 80) ranges['Excellent (80-100%)']++
      else if (percentage >= 60) ranges['Good (60-79%)']++
      else if (percentage >= 40) ranges['Fair (40-59%)']++
      else ranges['Poor (<40%)']++
    })
    
    return Object.entries(ranges).map(([name, value]) => ({ name, value }))
  }

  const calculateWeaknessData = () => {
    const weaknessCount: Record<string, number> = {}
    
    allStudentAnalytics.forEach(analytics => {
      analytics.weaknesses.forEach(weakness => {
        weaknessCount[weakness] = (weaknessCount[weakness] || 0) + 1
      })
    })
    
    const chartData = Object.entries(weaknessCount)
      .map(([name, value]) => ({
        name,
        value,
        percentage: Math.round((value / allStudentAnalytics.length) * 100)
      }))
      .sort((a, b) => b.value - a.value)
    
    return chartData
  }
  
  const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444']
  const WEAKNESS_COLORS = ['#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16', '#22c55e']

  const stats = calculateStats()
  const selectedExam = exams.find(exam => exam.id.toString() === selectedExamId)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Exam Results Analytics
        </CardTitle>
        <CardDescription>
          Comprehensive performance analysis and student insights
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
          {selectedExam && results.length > 0 && (
            <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-semibold text-blue-900 mb-1">{selectedExam.title}</h4>
                  <p className="text-sm text-blue-700">
                    {selectedExam.document_title} • {selectedExam.total_questions} questions • Created {new Date(selectedExam.created_at).toLocaleDateString()}
                  </p>
                </div>
                <Button variant="outline" size="sm" onClick={exportToCSV} className="gap-2">
                  <Download className="h-4 w-4" />
                  Export CSV
                </Button>
              </div>
            </div>
          )}

          {/* Statistics Cards */}
          {filteredResults.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="border-l-4 border-l-blue-500">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Users className="h-4 w-4 text-blue-500" />
                    <span className="text-sm font-medium text-gray-600">Total Students</span>
                  </div>
                  <div className="text-3xl font-bold text-gray-900">{stats.totalStudents}</div>
                  <p className="text-xs text-gray-500 mt-1">Completed exam</p>
                </CardContent>
              </Card>
              
              <Card className="border-l-4 border-l-green-500">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="h-4 w-4 text-green-500" />
                    <span className="text-sm font-medium text-gray-600">Pass Rate</span>
                  </div>
                  <div className="text-3xl font-bold text-gray-900">{stats.passRate}%</div>
                  <p className="text-xs text-gray-500 mt-1">≥60% threshold</p>
                </CardContent>
              </Card>
              
              <Card className="border-l-4 border-l-purple-500">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <BarChart3 className="h-4 w-4 text-purple-500" />
                    <span className="text-sm font-medium text-gray-600">Avg. Score</span>
                  </div>
                  <div className="text-3xl font-bold text-gray-900">{stats.avgScore}</div>
                  <p className="text-xs text-gray-500 mt-1">Out of 10 questions</p>
                </CardContent>
              </Card>
              
              <Card className="border-l-4 border-l-orange-500">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="h-4 w-4 text-orange-500" />
                    <span className="text-sm font-medium text-gray-600">Avg. Time</span>
                  </div>
                  <div className="text-3xl font-bold text-gray-900">{stats.avgTime}</div>
                  <p className="text-xs text-gray-500 mt-1">Per exam</p>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Charts Row */}
          {filteredResults.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Score Distribution Pie Chart */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Score Distribution</CardTitle>
                  <CardDescription>Performance breakdown by grade range</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={getScoreDistributionData()}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, value }: any) => (value as number) > 0 ? `${value}` : ''}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {getScoreDistributionData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Weakness Areas */}
              {allStudentAnalytics.length > 0 && calculateWeaknessData().length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Common Weaknesses</CardTitle>
                    <CardDescription>Topics needing improvement</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={250}>
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
                            <Cell key={`cell-${index}`} fill={WEAKNESS_COLORS[index % WEAKNESS_COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value: number) => [`${value} students`, 'Count']} />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Filters and Search */}
          {results.length > 0 && (
            <div className="flex flex-wrap gap-4 items-end p-4 bg-gray-50 rounded-lg border">
              <div className="flex-1 min-w-[200px]">
                <Label htmlFor="search" className="mb-2 block">Search Students</Label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="search"
                    placeholder="Name or ID..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9"
                  />
                </div>
              </div>
              
              <div className="min-w-[150px]">
                <Label htmlFor="scoreFilter" className="mb-2 block">Filter by Score</Label>
                <Select value={scoreFilter} onValueChange={(value: any) => setScoreFilter(value)}>
                  <SelectTrigger id="scoreFilter">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Scores</SelectItem>
                    <SelectItem value="high">High (≥70%)</SelectItem>
                    <SelectItem value="medium">Medium (40-69%)</SelectItem>
                    <SelectItem value="low">Low (&lt;40%)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button 
                variant="outline" 
                onClick={() => {
                  setSearchQuery('')
                  setScoreFilter('all')
                  setSortField('score')
                  setSortOrder('desc')
                }}
              >
                <Filter className="h-4 w-4 mr-2" />
                Reset Filters
              </Button>
            </div>
          )}

          {/* Results Table */}
          {filteredResults.length > 0 ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">
                  Student Results ({filteredResults.length})
                </h3>
              </div>
              
              <div className="overflow-x-auto rounded-lg border">
                <table className="w-full border-collapse">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="border-b px-4 py-3 text-left">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleSort('name')}
                          className="font-semibold hover:bg-gray-200"
                        >
                          Student
                          <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                      </th>
                      <th className="border-b px-4 py-3 text-left">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleSort('score')}
                          className="font-semibold hover:bg-gray-200"
                        >
                          Score
                          <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                      </th>
                      <th className="border-b px-4 py-3 text-left font-semibold">Questions</th>
                      <th className="border-b px-4 py-3 text-left">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleSort('time')}
                          className="font-semibold hover:bg-gray-200"
                        >
                          Time
                          <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                      </th>
                      <th className="border-b px-4 py-3 text-left font-semibold">Status</th>
                      <th className="border-b px-4 py-3 text-left font-semibold">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white">
                    {filteredResults.map((result, index) => (
                      <React.Fragment key={`student-${result.student_id}-${result.exam_session_id}`}>
                        {/* Main Row */}
                        <tr className={`hover:bg-gray-50 transition-colors ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'}`}>
                          <td className="border-b px-4 py-3">
                            <div>
                              <div className="font-medium text-gray-900">{result.student_name}</div>
                              <div className="text-sm text-gray-500">ID: {result.student_id}</div>
                            </div>
                          </td>
                          <td className="border-b px-4 py-3">
                            <div className="flex items-center gap-2">
                              <Badge 
                                variant={result.score >= result.total_questions * 0.7 ? "default" : "destructive"}
                                className="font-semibold"
                              >
                                {result.score}/{result.total_questions}
                              </Badge>
                              <span className="text-sm font-medium text-gray-600">
                                ({Math.round((result.score / result.total_questions) * 100)}%)
                              </span>
                            </div>
                          </td>
                          <td className="border-b px-4 py-3 text-gray-700">
                            {result.questions_answered}
                          </td>
                          <td className="border-b px-4 py-3">
                            {result.completed_at && result.started_at ? (
                              (() => {
                                const milliseconds = new Date(result.completed_at).getTime() - new Date(result.started_at).getTime()
                                const totalSeconds = Math.round(milliseconds / 1000)
                                const minutes = Math.floor(totalSeconds / 60)
                                const seconds = totalSeconds % 60
                                
                                return <span className="text-sm text-gray-700">{minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`}</span>
                              })()
                            ) : (
                              <span className="text-sm text-gray-400">-</span>
                            )}
                          </td>
                          <td className="border-b px-4 py-3">
                            {result.completed_at ? (
                              <Badge variant="default" className="bg-green-100 text-green-800 border-green-300">Completed</Badge>
                            ) : (
                              <Badge variant="secondary">In Progress</Badge>
                            )}
                          </td>
                          <td className="border-b px-4 py-3">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleToggleStudent(result.student_id, result.exam_session_id)}
                              disabled={isLoadingAnalytics && expandedStudent !== result.student_id}
                            >
                              {expandedStudent === result.student_id ? 'Hide' : 'View'} Details
                            </Button>
                          </td>
                        </tr>

                        {/* Expanded Analytics Row */}
                        {expandedStudent === result.student_id && studentAnalytics && (
                          <tr>
                            <td colSpan={6} className="border-b bg-gradient-to-br from-gray-50 to-blue-50/30 p-6">
                              {isLoadingAnalytics ? (
                                <div className="text-center py-4">Loading analytics...</div>
                              ) : (
                                <div className="space-y-6">
                                  {/* Overall Performance */}
                                  <div>
                                    <h4 className="font-semibold mb-3 text-lg">📊 Overall Performance</h4>
                                    <div className="grid grid-cols-3 gap-4">
                                      <div className="p-4 bg-white rounded-lg border shadow-sm">
                                        <div className="text-sm text-gray-600 mb-1">Correct Answers</div>
                                        <div className="text-2xl font-bold text-blue-600">{studentAnalytics.total_correct}/{studentAnalytics.total_questions}</div>
                                      </div>
                                      <div className="p-4 bg-white rounded-lg border shadow-sm">
                                        <div className="text-sm text-gray-600 mb-1">Overall Score</div>
                                        <div className="text-2xl font-bold text-purple-600">{Math.round(studentAnalytics.overall_percentage)}%</div>
                                      </div>
                                      <div className="p-4 bg-white rounded-lg border shadow-sm">
                                        <div className="text-sm text-gray-600 mb-1">Performance</div>
                                        <div className="text-xl font-bold">
                                          {studentAnalytics.overall_percentage >= 80 ? '🌟 Excellent' : 
                                          studentAnalytics.overall_percentage >= 60 ? '✅ Good' : 
                                          studentAnalytics.overall_percentage >= 40 ? '⚠️ Fair' : '❌ Needs Help'}
                                        </div>
                                      </div>
                                    </div>
                                  </div>

                                  {/* Strengths and Weaknesses */}
                                  <div className="grid grid-cols-2 gap-4">
                                    {studentAnalytics.strengths && studentAnalytics.strengths.length > 0 && (
                                      <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                                        <h4 className="font-semibold mb-2 text-green-800 flex items-center gap-2">
                                          💪 Strengths
                                        </h4>
                                        <div className="flex flex-wrap gap-2">
                                          {studentAnalytics.strengths.map((topic, i) => (
                                            <Badge key={i} className="bg-green-100 text-green-800 border-green-300">
                                              {topic}
                                            </Badge>
                                          ))}
                                        </div>
                                      </div>
                                    )}

                                    {studentAnalytics.weaknesses && studentAnalytics.weaknesses.length > 0 && (
                                      <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                                        <h4 className="font-semibold mb-2 text-red-800 flex items-center gap-2">
                                          📚 Areas for Improvement
                                        </h4>
                                        <div className="flex flex-wrap gap-2">
                                          {studentAnalytics.weaknesses.map((topic, i) => (
                                            <Badge key={i} className="bg-red-100 text-red-800 border-red-300">
                                              {topic}
                                            </Badge>
                                          ))}
                                        </div>
                                      </div>
                                    )}
                                  </div>

                                  {/* Topic Breakdown */}
                                  <div>
                                    <h4 className="font-semibold mb-3 text-lg">📈 Performance by Topic</h4>
                                    <div className="overflow-x-auto rounded-lg border bg-white">
                                      <table className="w-full text-sm">
                                        <thead className="bg-gray-50">
                                          <tr>
                                            <th className="border-b px-4 py-2 text-left font-semibold">Topic</th>
                                            <th className="border-b px-4 py-2 text-center font-semibold">Score</th>
                                            <th className="border-b px-4 py-2 text-center font-semibold">Percentage</th>
                                            <th className="border-b px-4 py-2 text-left font-semibold">Level</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {studentAnalytics.topic_breakdown.map((topic, i) => (
                                            <tr key={i} className="hover:bg-gray-50">
                                              <td className="border-b px-4 py-2">{topic.topic_name}</td>
                                              <td className="border-b px-4 py-2 text-center">
                                                {topic.correct_answers}/{topic.questions_answered}
                                              </td>
                                              <td className="border-b px-4 py-2 text-center">
                                                <span className={`font-semibold ${
                                                  topic.percentage >= 80 ? 'text-green-600' :
                                                  topic.percentage >= 60 ? 'text-blue-600' :
                                                  topic.percentage >= 40 ? 'text-yellow-600' :
                                                  'text-red-600'
                                                }`}>
                                                  {Math.round(topic.percentage)}%
                                                </span>
                                              </td>
                                              <td className="border-b px-4 py-2">
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
          ) : results.length > 0 ? (
            <div className="text-center py-8 bg-gray-50 rounded-lg border">
              <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-3" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No Results Match Your Filters
              </h3>
              <p className="text-gray-500 mb-4">
                Try adjusting your search or filter criteria
              </p>
              <Button 
                variant="outline" 
                onClick={() => {
                  setSearchQuery('')
                  setScoreFilter('all')
                }}
              >
                Clear Filters
              </Button>
            </div>
          ) : selectedExamId ? (
            <div className="text-center py-12 bg-gray-50 rounded-lg border">
              <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <BarChart3 className="h-8 w-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No Results Found
              </h3>
              <p className="text-gray-500">
                No students have taken this exam yet.
              </p>
            </div>
          ) : (
            <div className="text-center py-12 bg-gradient-to-br from-gray-50 to-blue-50/30 rounded-lg border">
              <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                <BarChart3 className="h-8 w-8 text-blue-500" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Select an Exam
              </h3>
              <p className="text-gray-500">
                Choose an exam from the dropdown above to view detailed results and analytics
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}