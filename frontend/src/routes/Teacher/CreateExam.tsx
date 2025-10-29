// frontend/src/routes/Teacher/CreateExam.tsx

import { useState } from "react";
import { useCreateExam, useDocuments } from "@/lib/queries";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { 
  Plus, 
  FileText, 
  CheckCircle2, 
  AlertCircle,
  Sparkles,
  BookOpen,
  Target,
  Zap
} from "lucide-react";
import DocumentsDropdown from "@/components/DocumentsDropdown";

export default function CreateExam() {
  const [formData, setFormData] = useState({
    documentId: "",
  });
  const [selectedDocName, setSelectedDocName] = useState("");

  const createExamMutation = useCreateExam();
  const { toast } = useToast();

  const handleInputChange = (field: string, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.documentId) {
      toast({
        title: "Validation Error",
        description: "Please select a document",
        variant: "destructive",
      });
      return;
    }

    try {
      const result = await createExamMutation.mutateAsync({
        document_id: formData.documentId,
      });

      if (result.success) {
        const message = result.reused
          ? `Exam created using ${result.questions} existing questions`
          : `Exam created with ${result.questions} new questions`;

        toast({
          title: "Exam Created Successfully! 🎉",
          //description: message,
        });

        setFormData({ documentId: "" });
        setSelectedDocName("");
      }
    } catch (error) {
      toast({
        title: "Creation Failed",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    }
  };

  return (
    <Card className="card-hover animate-fade-in">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Plus className="h-5 w-5 text-purple-600" />
          Create New Exam
        </CardTitle>
        <CardDescription>
          Create an adaptive exam with automatically selected questions
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Document Selection */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-gray-700">Step 1: Select Document</h3>
              {formData.documentId && (
                <CheckCircle2 className="h-5 w-5 text-green-600 animate-scale-in" />
              )}
            </div>
            
            <DocumentsDropdown
              onSelect={(doc) => {
                handleInputChange("documentId", doc.id);
                setSelectedDocName(doc.label);
              }}
              value={formData.documentId}
              disabled={createExamMutation.isPending}
            />

            {selectedDocName && (
              <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg animate-fade-in">
                <div className="flex items-center gap-2 text-sm text-purple-800">
                  <FileText className="h-4 w-4" />
                  <span className="font-medium">Selected:</span>
                  <span>{selectedDocName}</span>
                </div>
              </div>
            )}
          </div>

          {/* Exam Configuration Info */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold text-gray-700">Step 2: Exam Configuration</h3>
              <Sparkles className="h-4 w-4 text-yellow-500" />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Total Questions */}
              <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <BookOpen className="h-5 w-5 text-blue-600" />
                  <span className="text-sm font-semibold text-blue-900">Total Questions</span>
                </div>
                <p className="text-3xl font-bold text-blue-700">10</p>
                <p className="text-xs text-blue-600 mt-1">Questions per exam</p>
              </div>

              {/* Difficulty Mix */}
              <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Target className="h-5 w-5 text-purple-600" />
                  <span className="text-sm font-semibold text-purple-900">Difficulty Mix</span>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-purple-700">Level 3</span>
                    <span className="font-bold text-purple-800">30%</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-purple-700">Level 4</span>
                    <span className="font-bold text-purple-800">30%</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-purple-700">Level 5</span>
                    <span className="font-bold text-purple-800">40%</span>
                  </div>
                </div>
              </div>

              {/* Adaptive System */}
              <div className="p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Zap className="h-5 w-5 text-green-600" />
                  <span className="text-sm font-semibold text-green-900">Adaptive</span>
                </div>
                <p className="text-xs text-green-700 leading-relaxed">
                  Questions are randomly selected from all difficulty levels for each student
                </p>
              </div>
            </div>
          </div>

          {/* Features List */}
          <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              Exam Features
            </h4>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                Automatically generates 10 questions per exam
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                Balanced difficulty distribution (3, 4, and 5)
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                AI-powered answer evaluation
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                Detailed analytics and performance tracking
              </li>
            </ul>
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={createExamMutation.isPending || !formData.documentId}
            className="w-full btn-hover h-12 text-lg shadow-lg"
          >
            {createExamMutation.isPending ? (
              <>
                <div className="spinner w-5 h-5 border-2 mr-2"></div>
                Creating Exam...
              </>
            ) : (
              <>
                <Plus className="h-5 w-5 mr-2" />
                Create Exam
              </>
            )}
          </Button>

          {/* Help Text */}
          {!formData.documentId && (
            <p className="text-center text-sm text-gray-500 animate-fade-in">
              Select a document to get started
            </p>
          )}
        </form>

        {/* Error Display */}
        {createExamMutation.isError && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg animate-fade-in">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-red-900 mb-1">Creation Failed</h4>
                <p className="text-sm text-red-600">
                  {createExamMutation.error?.message || "Unknown error occurred"}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Success Message */}
        {createExamMutation.isSuccess && !createExamMutation.isPending && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg animate-scale-in">
            <div className="flex items-start gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-green-900 mb-1">Exam Ready!</h4>
                <p className="text-sm text-green-700">
                  Your exam has been created and is ready for students. They can now take the exam from their dashboard.
                </p>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}