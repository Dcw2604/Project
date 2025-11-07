// frontend/src/routes/Teacher/UploadDocument.tsx

import { useState } from "react";
import { useUploadDocument } from "@/lib/queries";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { 
  Upload, 
  FileText, 
  CheckCircle2, 
  X, 
  AlertCircle,
  FileCheck,
  Sparkles
} from "lucide-react";

export default function UploadDocument() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [gradingInstructions, setGradingInstructions] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const uploadMutation = useUploadDocument();
  const { toast } = useToast();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      validateAndSetFile(file);
    }
  };

  const validateAndSetFile = (file: File) => {
    // Check file type
    const validTypes = ['.pdf', '.txt', '.doc', '.docx'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!validTypes.includes(fileExtension)) {
      toast({
        title: "Invalid Files Type",
        description: "Please upload PDF, TXT, DOC, or DOCX files",
        variant: "destructive",
      });
      return;
    }

    // Check file size (max 20MB)
    if (file.size > 20 * 1024 * 1024) {
      toast({
        title: "Files Too Large",
        description: "Please upload files smaller than 20MB",
        variant: "destructive",
      });
      return;
    }

    setSelectedFile(file);
    toast({
      title: "Files Selected",
      description: `${file.name} ready to upload`,
    });
  };

  // Drag and drop handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const file = e.dataTransfer.files?.[0];
    if (file) {
      validateAndSetFile(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedFile) {
      toast({
        title: "No Files Selected",
        description: "Please select a files to upload",
        variant: "destructive",
      });
      return;
    }

    try {
      const result = await uploadMutation.mutateAsync({
        file: selectedFile,
        gradingInstructions,
      });

      if (result.success) {
        toast({
          title: "Upload Successful! 🎉",
          description: `Documents uploaded and ${result.questions_generated} questions generated!`,
        });

        setSelectedFile(null);
        setGradingInstructions("");
        
        // Reset file input
        const fileInput = document.getElementById('file-upload') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      }
    } catch (error) {
      toast({
        title: "Upload Failed",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    const fileInput = document.getElementById('file-upload') as HTMLInputElement;
    if (fileInput) fileInput.value = '';
  };

  return (
    <Card className="card-hover animate-fade-in">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5 text-blue-600" />
          Upload Documents
        </CardTitle>
        <CardDescription>
          Upload documents to automatically generate quizzes questions
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Drag & Drop Area */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-all ${
              isDragging
                ? 'border-blue-500 bg-blue-50'
                : selectedFile
                ? 'border-green-500 bg-green-50'
                : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
            }`}
          >
            {!selectedFile ? (
              <div className="animate-fade-in">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Upload className="h-8 w-8 text-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {isDragging ? 'Drop your files here' : 'Upload Documents'}
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Drag and drop your files here, or click to browse
                </p>
                <Input
                  id="file-upload"
                  type="file"
                  accept=".pdf,.txt,.doc,.docx"
                  onChange={handleFileChange}
                  disabled={uploadMutation.isPending}
                  className="hidden"
                />
                <Label
                  htmlFor="file-upload"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer transition-colors btn-hover"
                >
                  <FileText className="h-4 w-4" />
                  Choose Files
                </Label>
                <p className="text-xs text-gray-500 mt-4">
                  Supported formats: PDF, TXT, DOC, DOCX (Max 20MB)
                </p>
              </div>
            ) : (
              <div className="animate-scale-in">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <FileCheck className="h-8 w-8 text-green-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Files Selected
                </h3>
                <div className="inline-flex items-center gap-3 px-4 py-3 bg-white border border-green-200 rounded-lg">
                  <FileText className="h-5 w-5 text-green-600" />
                  <div className="text-left">
                    <p className="font-medium text-gray-900">{selectedFile.name}</p>
                    <p className="text-sm text-gray-500">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={removeFile}
                    className="ml-2 p-1 hover:bg-red-100 rounded-full transition-colors"
                  >
                    <X className="h-5 w-5 text-red-600" />
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Grading Instructions */}
          <div className="space-y-2">
            <Label htmlFor="grading-instructions" className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-purple-600" />
              Grading Instructions (Optional)
            </Label>
            <Textarea
              id="grading-instructions"
              placeholder="הוסף הערכות לבדיקת התשובות... למשל: שים דגש על מורכבות הפתרון, בדוק את הדיוק במונחים טכניים"
              value={gradingInstructions}
              onChange={(e) => setGradingInstructions(e.target.value)}
              disabled={uploadMutation.isPending}
              className="min-h-[100px] resize-y"
              dir="rtl"
            />
            <p className="text-sm text-gray-500 flex items-center gap-1" dir="rtl">
              <AlertCircle className="h-4 w-4" />
              ספק הנחיות איך Gemini צריך להעריך תשובות של תלמידים
            </p>
          </div>

          {/* Info Box */}
          {selectedFile && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg animate-fade-in">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h4 className="font-semibold text-blue-900 mb-1">Ready to Process</h4>
                  <p className="text-sm text-blue-800">
                    Your Documents will be analyzed by AI to automatically generate quizzes questions
                    across different difficulty levels.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={!selectedFile || uploadMutation.isPending}
            className="w-full btn-hover h-12 text-lg shadow-lg"
          >
            {uploadMutation.isPending ? (
              <>
                <div className="spinner w-5 h-5 border-2 mr-2"></div>
                Processing Documents...
              </>
            ) : (
              <>
                <Upload className="h-5 w-5 mr-2" />
                Upload & Generate Questions
              </>
            )}
          </Button>

          {/* Progress/Success */}
          {uploadMutation.isPending && (
            <div className="space-y-2 animate-fade-in">
              <div className="flex items-center justify-between text-sm text-gray-600">
                <span>Analyzing Documents...</span>
                <span className="animate-pulse">Processing</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-blue-500 to-purple-500 shimmer"></div>
              </div>
            </div>
          )}
        </form>

        {/* Error Display */}
        {uploadMutation.isError && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg animate-fade-in">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-red-900 mb-1">Upload Failed</h4>
                <p className="text-sm text-red-600">
                  {uploadMutation.error?.message || "Unknown error occurred"}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Success Message */}
        {uploadMutation.isSuccess && !uploadMutation.isPending && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg animate-scale-in">
            <div className="flex items-start gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-green-900 mb-1">Success!</h4>
                <p className="text-sm text-green-700">
                  Questions have been generated and saved. You can now create quizzes using this Documents.
                </p>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}