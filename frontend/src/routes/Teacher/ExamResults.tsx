import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { BarChart3, Users, Clock, TrendingUp, RefreshCw } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface ExamResult {
  student_name: string
  student_id: number
  score: number
  total_questions: number
  questions_answered: number
  completed_at: string | null
  started_at: string
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
        setResults(data.results)
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
        return sum + (end.getTime() - start.getTime()) / 1000 / 60 // minutes
      }
      return sum
    }, 0)
    const avgTime = Math.round((totalTime / results.length) * 10) / 10
    
    return {
      avgScore,
      totalStudents: results.length,
      avgTime
    }
  }

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
                      <th className="border border-gray-200 px-4 py-2 text-left">Completion Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((result, index) => (
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
                        </td>
                        <td className="border border-gray-200 px-4 py-2">
                          {result.questions_answered}/{result.total_questions}
                        </td>
                        <td className="border border-gray-200 px-4 py-2">
                          {result.completed_at ? (
                            <Badge variant="default">Completed</Badge>
                          ) : (
                            <Badge variant="secondary">In Progress</Badge>
                          )}
                        </td>
                      </tr>
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
        </div>
      </CardContent>
    </Card>
  )
}