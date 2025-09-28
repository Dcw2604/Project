import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Play, Clock, FileText } from 'lucide-react'
import type { ExamCard as ExamCardType } from '@/lib/types'

interface ExamCardProps {
  exam: ExamCardType
  onStart: (examId: string | number) => void
  isLoading?: boolean
}

export default function ExamCard({ exam, onStart, isLoading = false }: ExamCardProps) {
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Unknown date'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'available':
        return 'bg-green-100 text-green-800'
      case 'in progress':
        return 'bg-blue-100 text-blue-800'
      case 'completed':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="text-lg">{exam.title}</CardTitle>
            <CardDescription>
              {exam.total_questions ? `${exam.total_questions} questions` : 'Questions not specified'}
            </CardDescription>
          </div>
          <Badge className={getStatusColor(exam.status)}>
            {exam.status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <FileText className="h-4 w-4" />
              {exam.total_questions || 'N/A'} questions
            </div>
            <div className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              {formatDate(exam.created_at)}
            </div>
          </div>
          
          <Button 
            onClick={() => onStart(exam.id)}
            disabled={isLoading}
            className="w-full"
          >
            <Play className="h-4 w-4 mr-2" />
            {isLoading ? 'Starting...' : 'Start Exam'}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
