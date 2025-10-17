import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { CheckCircle, XCircle } from 'lucide-react' 
import type { Question } from '@/lib/types'

interface QuestionCardProps {
  question: Question
  questionNumber: number
  totalQuestions: number
  onSubmit: (answer: string) => void
  isLoading: boolean
  currentAnswer: string
}

export default function QuestionCard({
  question,
  questionNumber,
  totalQuestions,
  onSubmit,
  isLoading,
  currentAnswer,
}: QuestionCardProps) {
  const [answer, setAnswer] = useState(currentAnswer)

  useEffect(() => {
    setAnswer(currentAnswer)
  }, [currentAnswer])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (answer.trim()) {
      onSubmit(answer.trim())
      setAnswer('') // Clear the answer box after submission
    }
  }

  const isMCQ = question.options && question.options.length > 0

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">
              Question {questionNumber} of {totalQuestions}
            </CardTitle>
            <CardDescription>
              {question.points && `${question.points} points`}
              {question.difficulty_level && ` • Level ${question.difficulty_level}`}
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            {question.type && (
              <Badge variant="secondary">
                {question.type.toUpperCase()}
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <div>
            <Label className="text-base font-medium">Question:</Label>
            <p className="mt-2 text-gray-900 text-lg leading-relaxed" dir="rtl">
              {question.question_text}
            </p>
          </div>


          <form onSubmit={handleSubmit} className="space-y-4">
            {isMCQ ? (
              <div className="space-y-3">
                <Label className="text-base font-medium">Choose your answer:</Label>
                <div className="space-y-2">
                  {question.options!.map((option, index) => (
                    <label
                      key={index}
                      className="flex items-center space-x-3 p-3 border rounded-md hover:bg-gray-50 cursor-pointer"
                    >
                      <input
                        type="radio"
                        name="answer"
                        value={option}
                        checked={answer === option}
                        onChange={(e) => setAnswer(e.target.value)}
                        className="h-4 w-4 text-blue-600"
                      />
                      <span className="text-gray-900">{option}</span>
                    </label>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <Label htmlFor="answer" className="text-base font-medium">
                  Your Answer:
                </Label>
                <Textarea
                  id="answer"
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Enter your answer here..."
                  className="text-base min-h-[120px] resize-y"
                  disabled={isLoading}
                  rows={5}
                />
              </div>
            )}

            <div className="flex justify-end">
              <Button
                type="submit"
                disabled={!answer.trim() || isLoading}
                className="min-w-[120px]"
              >
                {isLoading ? 'Submitting...' : 'Submit Answer'}
              </Button>
            </div>
          </form>
        </div>
      </CardContent>
    </Card>
  )
}