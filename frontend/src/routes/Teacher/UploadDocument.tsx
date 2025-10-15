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
import { Upload, FileText } from "lucide-react";

export default function UploadDocument() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [gradingInstructions, setGradingInstructions] = useState("");
  const uploadMutation = useUploadDocument();
  const { toast } = useToast();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    try {
      const result = await uploadMutation.mutateAsync({
        file: selectedFile,
        gradingInstructions: gradingInstructions.trim() || undefined,
      });

      if (result.success) {
        const filename = result.filename || selectedFile.name;
        toast({
          title: "Upload Successful",
          description: `Document "${filename}" uploaded successfully`,
        });
        setSelectedFile(null);
        setGradingInstructions("");
        // Reset file input
        const fileInput = document.getElementById(
          "file-upload"
        ) as HTMLInputElement;
        if (fileInput) fileInput.value = "";
      } else {
        throw new Error("Upload failed");
      }
    } catch (error) {
      toast({
        title: "Upload Failed",
        description:
          error instanceof Error ? error.message : "Failed to upload document",
        variant: "destructive",
      });
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5" />
          Upload Document
        </CardTitle>
        <CardDescription>
          Upload a document to generate questions and create exams
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="file-upload">Select Document</Label>
            <Input
              id="file-upload"
              type="file"
              accept=".pdf,.txt,.doc,.docx"
              onChange={handleFileChange}
              disabled={uploadMutation.isPending}
            />
            {selectedFile && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <FileText className="h-4 w-4" />
                {selectedFile.name} (
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
              </div>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="grading-instructions">
              Grading Instructions (Optional)
            </Label>
            <Input
              id="grading-instructions"
              placeholder="הוסף הערכות לבדיקת התשובות... למשל: שים דגש על מורכבות הפתרון, בדוק את הדיוק במונחים טכניים"
              value={gradingInstructions}
              onChange={(e) => setGradingInstructions(e.target.value)}
              disabled={uploadMutation.isPending}
              className="min-h-[80px]"
            />
            <p className="text-sm text-muted-foreground">
              ספק הנחיות איך Gemini צריך להעריך תשובות של תלמידים
            </p>
          </div>

          <Button
            type="submit"
            disabled={!selectedFile || uploadMutation.isPending}
            className="w-full"
          >
            {uploadMutation.isPending ? "Uploading..." : "Upload Document"}
          </Button>
        </form>

        {uploadMutation.isError && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">
              Upload failed: {uploadMutation.error?.message || "Unknown error"}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
