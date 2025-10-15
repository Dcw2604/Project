import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { FileText, RefreshCw, Eye, CheckCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface Question {
  id: number;
  question_text: string;
  correct_answer?: string;
  sample_answer?: string;
  difficulty_level: number;
  question_type: string;
  explanation?: string;
}

interface Exam {
  id: number;
  title: string;
  document_title: string;
  total_questions: number;
  created_at: string;
}

export default function ViewQuestions() {
  const [exams, setExams] = useState<Exam[]>([]);
  const [selectedExamId, setSelectedExamId] = useState("");
  const [questions, setQuestions] = useState<Question[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingExams, setIsLoadingExams] = useState(true);
  const { toast } = useToast();

  // Fetch exams on component mount
  useEffect(() => {
    fetchExams();
  }, []);

  const fetchExams = async () => {
    setIsLoadingExams(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/api/exams/");
      const data = await response.json();

      if (data.success) {
        setExams(data.exams);
      } else {
        toast({
          title: "Error",
          description: "Failed to fetch exams",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch exams",
        variant: "destructive",
      });
    } finally {
      setIsLoadingExams(false);
    }
  };

  const fetchQuestions = async () => {
    if (!selectedExamId) return;

    setIsLoading(true);
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/exams/${selectedExamId}/questions/`
      );
      const data = await response.json();

      if (data.success) {
        setQuestions(data.questions);
      } else {
        toast({
          title: "Error",
          description: "Failed to fetch questions",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch questions",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const selectedExam = exams.find(
    (exam) => exam.id.toString() === selectedExamId
  );

  const getDifficultyBadgeColor = (level: number) => {
    switch (level) {
      case 3:
        return "bg-blue-100 text-blue-800";
      case 4:
        return "bg-yellow-100 text-yellow-800";
      case 5:
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getQuestionTypeBadgeColor = (type: string) => {
    switch (type) {
      case "open_ended":
        return "bg-green-100 text-green-800";
      case "multiple_choice":
        return "bg-purple-100 text-purple-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          View Questions
        </CardTitle>
        <CardDescription>
          View all questions created for an exam and see which ones are selected
          for students
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
                  <SelectValue
                    placeholder={
                      isLoadingExams ? "Loading exams..." : "Choose an exam"
                    }
                  />
                </SelectTrigger>
                <SelectContent>
                  {exams.map((exam) => (
                    <SelectItem key={exam.id} value={exam.id.toString()}>
                      <div className="flex flex-col">
                        <span className="font-medium">{exam.title}</span>
                        <span className="text-sm text-gray-500">
                          {exam.document_title} • {exam.total_questions}{" "}
                          questions
                        </span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                onClick={fetchQuestions}
                disabled={isLoading || !selectedExamId}
              >
                {isLoading ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
                {isLoading ? "Loading..." : "View Questions"}
              </Button>
            </div>
          </div>

          {/* Selected Exam Info */}
          {selectedExam && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-blue-900">
                    {selectedExam.title}
                  </h3>
                  <p className="text-sm text-blue-700">
                    Document: {selectedExam.document_title} • Total Questions:{" "}
                    {selectedExam.total_questions} • Created:{" "}
                    {new Date(selectedExam.created_at).toLocaleDateString()}
                  </p>
                </div>
                <Badge variant="outline" className="bg-blue-100 text-blue-800">
                  {questions.length} Questions Loaded
                </Badge>
              </div>
            </div>
          )}

          {/* Questions List */}
          {questions.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">Exam Questions</h3>
                <div className="text-sm text-gray-500">
                  Showing {questions.length} questions (10 will be randomly
                  selected for students)
                </div>
              </div>

              <div className="grid gap-4">
                {questions.map((question, index) => (
                  <Card
                    key={question.id}
                    className="border-l-4 border-l-blue-500"
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge
                              className={getDifficultyBadgeColor(
                                question.difficulty_level
                              )}
                            >
                              Level {question.difficulty_level}
                            </Badge>
                            <Badge
                              className={getQuestionTypeBadgeColor(
                                question.question_type
                              )}
                            >
                              {question.question_type === "open_ended"
                                ? "Open Ended"
                                : "Multiple Choice"}
                            </Badge>
                          </div>
                          <CardTitle className="text-base">
                            Question {index + 1}
                          </CardTitle>
                          <CardDescription className="text-sm">
                            {question.question_text}
                          </CardDescription>
                        </div>
                        <div className="flex items-center gap-2">
                          <CheckCircle className="h-5 w-5 text-green-500" />
                          <span className="text-sm text-green-600 font-medium">
                            Available
                          </span>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="space-y-3">
                        {question.correct_answer && (
                          <div>
                            <Label className="text-sm font-medium text-gray-700">
                              Correct Answer:
                            </Label>
                            <p className="text-sm text-gray-600 mt-1 p-2 bg-green-50 border border-green-200 rounded">
                              {question.correct_answer}
                            </p>
                          </div>
                        )}

                        {question.sample_answer &&
                          question.sample_answer !==
                            question.correct_answer && (
                            <div>
                              <Label className="text-sm font-medium text-gray-700">
                                Sample Answer:
                              </Label>
                              <p className="text-sm text-gray-600 mt-1 p-2 bg-blue-50 border border-blue-200 rounded">
                                {question.sample_answer}
                              </p>
                            </div>
                          )}

                        {question.explanation && (
                          <div>
                            <Label className="text-sm font-medium text-gray-700">
                              Explanation:
                            </Label>
                            <p className="text-sm text-gray-600 mt-1 p-2 bg-gray-50 border border-gray-200 rounded">
                              {question.explanation}
                            </p>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {selectedExamId && questions.length === 0 && !isLoading && (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No questions found for this exam</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
