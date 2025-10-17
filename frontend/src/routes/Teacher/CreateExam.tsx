import { useState } from 'react'
import { useCreateExam, useDocuments } from '@/lib/queries'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useToast } from '@/hooks/use-toast'
import { Plus } from 'lucide-react'
import DocumentsDropdown from '@/components/DocumentsDropdown'

export default function CreateExam() {
  const [formData, setFormData] = useState({
    documentId: ''
  })
  
  const createExamMutation = useCreateExam()
  const { toast } = useToast()

  const handleInputChange = (field: string, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.documentId) {
      toast({
        title: "Validation Error",
        description: "Please fill in all required fields",
        variant: "destructive",
      })
      return
    }

    try {
      const result = await createExamMutation.mutateAsync({
        document_id: formData.documentId,
        levels: [3, 4, 5], // Always use all levels
        questions_per_level: 10 // Always create 10 questions total
      })

      if (result.success) {
        toast({
          title: "Exam Created Successfully",
          description: `Exam has been created with 10 questions from all difficulty levels.`,
        })

        // Reset form
        setFormData({
          documentId: ''
        })
      }
    } catch (error) {
      toast({
        title: "Creation Failed",
        description: error instanceof Error ? error.message : 'Failed to create exam',
        variant: "destructive",
      })
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Plus className="h-5 w-5" />
          Create Exam
        </CardTitle>
        <CardDescription>
          Create a new exam with 10 questions from all difficulty levels
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">

          <DocumentsDropdown
            onSelect={(doc) => handleInputChange('documentId', doc.id)}
            value={formData.documentId}
            disabled={createExamMutation.isPending}
          />

          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <h4 className="font-medium text-blue-900 mb-2">Exam Configuration</h4>
            <p className="text-sm text-blue-800">
              This exam will automatically include 10 questions from all difficulty levels (3, 4, and 5) based on the selected document.
            </p>
          </div>

          <Button
            type="submit"
            disabled={createExamMutation.isPending || !formData.documentId}
            className="w-full"
          >
            {createExamMutation.isPending ? 'Creating...' : 'Create Exam'}
          </Button>
        </form>

        {createExamMutation.isError && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">
              Creation failed: {createExamMutation.error?.message || 'Unknown error'}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}