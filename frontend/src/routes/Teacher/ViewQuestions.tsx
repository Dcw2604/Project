// frontend/src/routes/Teacher/ViewQuestions.tsx

import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { 
  FileText, 
  RefreshCw, 
  Eye, 
  CheckCircle, 
  Search,
  Filter,
  BookOpen,
  Target,
  Lightbulb
} from "lucide-react";
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
  const [filteredQuestions, setFilteredQuestions] = useState<Question[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingExams, setIsLoadingExams] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [difficultyFilter, setDifficultyFilter] = useState<string>("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const { toast } = useToast();

  useEffect(() => {
    fetchExams();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [questions, searchQuery, difficultyFilter, typeFilter]);

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
        toast({
          title: "Questions Loaded",
          description: `Found ${data.questions.length} questions`,
        });
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

  const applyFilters = () => {
    let filtered = [...questions];

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(q =>
        q.question_text.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Difficulty filter
    if (difficultyFilter !== "all") {
      filtered = filtered.filter(q =>
        q.difficulty_level.toString() === difficultyFilter
      );
    }

    // Type filter
    if (typeFilter !== "all") {
      filtered = filtered.filter(q =>
        q.question_type === typeFilter
      );
    }

    setFilteredQuestions(filtered);
  };

  const selectedExam = exams.find(
    (exam) => exam.id.toString() === selectedExamId
  );

  const getDifficultyBadge = (level: number) => {
    const configs = {
      1: { color: "bg-blue-100 text-blue-800 border-blue-300", label: "Level 1 - Easy" },
      2: { color: "bg-yellow-100 text-yellow-800 border-yellow-300", label: "Level 2 - Medium" },
      3: { color: "bg-red-100 text-red-800 border-red-300", label: "Level 3 - Hard" },
    };
    return configs[level as 1 | 2 | 3] || { color: "bg-gray-100 text-gray-800", label: `Level ${level}` };
  };

  const getQuestionTypeBadge = (type: string) => {
    const configs = {
      open_ended: { color: "bg-green-100 text-green-800 border-green-300", label: "Open Ended", icon: BookOpen },
      multiple_choice: { color: "bg-purple-100 text-purple-800 border-purple-300", label: "Multiple Choice", icon: Target },
    };
    return configs[type as keyof typeof configs] || { color: "bg-gray-100 text-gray-800", label: type, icon: FileText };
  };

  const difficultyStats = {
    level1: questions.filter(q => q.difficulty_level === 1).length,
    level2: questions.filter(q => q.difficulty_level === 2).length,
    level3: questions.filter(q => q.difficulty_level === 3).length,
  };

  return (
    <Card className="card-hover animate-fade-in">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-indigo-600" />
          View Questions
        </CardTitle>
        <CardDescription>
          Browse and filter all questions available for exams
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
                          {exam.document_title} • {exam.total_questions} questions
                        </span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                onClick={fetchQuestions}
                disabled={isLoading || !selectedExamId}
                className="btn-hover"
              >
                {isLoading ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
                {isLoading ? "Loading..." : "View"}
              </Button>
            </div>
          </div>

          {/* Selected Exam Info */}
          {selectedExam && (
            <div className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg animate-fade-in">
              <div className="flex items-center justify-between flex-wrap gap-3">
                <div>
                  <h3 className="font-semibold text-indigo-900 mb-1">
                    {selectedExam.title}
                  </h3>
                  <p className="text-sm text-indigo-700">
                    {selectedExam.document_title} • Created{" "}
                    {new Date(selectedExam.created_at).toLocaleDateString()}
                  </p>
                </div>
                <Badge className="bg-indigo-100 text-indigo-800 border-indigo-300">
                  {questions.length} Questions
                </Badge>
              </div>
            </div>
          )}

          {/* Stats Cards */}
          {questions.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 stagger-fade-in">
              <Card className="card-hover bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-700">{difficultyStats.level1}</div>
                    <div className="text-sm text-blue-600 mt-1">Level 1 - Easy</div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="card-hover bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-yellow-700">{difficultyStats.level2}</div>
                    <div className="text-sm text-yellow-600 mt-1">Level 2 - Medium</div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="card-hover bg-gradient-to-br from-red-50 to-red-100 border-red-200">
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-red-700">{difficultyStats.level3}</div>
                    <div className="text-sm text-red-600 mt-1">Level 3 - Hard</div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="card-hover bg-gradient-to-br from-gray-50 to-gray-100 border-gray-200">
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-gray-700">{questions.length}</div>
                    <div className="text-sm text-gray-600 mt-1">Total Questions</div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Filters */}
          {questions.length > 0 && (
            <div className="flex flex-wrap gap-3 p-4 bg-gray-50 rounded-lg border animate-fade-in">
              <div className="flex-1 min-w-[200px]">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search questions..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9"
                  />
                </div>
              </div>
              
              <Select value={difficultyFilter} onValueChange={setDifficultyFilter}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Difficulty" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Levels</SelectItem>
                  <SelectItem value="1">Level 1</SelectItem>
                  <SelectItem value="2">Level 2</SelectItem>
                  <SelectItem value="3">Level 3</SelectItem>
                </SelectContent>
              </Select>
              
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="open_ended">Open Ended</SelectItem>
                  <SelectItem value="multiple_choice">Multiple Choice</SelectItem>
                </SelectContent>
              </Select>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setSearchQuery("");
                  setDifficultyFilter("all");
                  setTypeFilter("all");
                }}
              >
                <Filter className="h-4 w-4 mr-2" />
                Reset
              </Button>
            </div>
          )}

          {/* Questions List */}
          {filteredQuestions.length > 0 ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">
                  Questions ({filteredQuestions.length})
                </h3>
                <p className="text-sm text-gray-500">
                  10 will be randomly selected per student
                </p>
              </div>

              <div className="grid gap-4 stagger-fade-in">
                {filteredQuestions.map((question, index) => {
                  const difficulty = getDifficultyBadge(question.difficulty_level);
                  const type = getQuestionTypeBadge(question.question_type);
                  const TypeIcon = type.icon;
                  
                  return (
                    <Card
                      key={question.id}
                      className="card-hover border-l-4 border-l-indigo-500"
                    >
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2 flex-wrap">
                              <Badge className={`${difficulty.color} border`}>
                                {difficulty.label}
                              </Badge>
                              <Badge className={`${type.color} border flex items-center gap-1`}>
                                <TypeIcon className="h-3 w-3" />
                                {type.label}
                              </Badge>
                            </div>
                            <CardTitle className="text-base flex items-center gap-2">
                              Question {index + 1}
                            </CardTitle>
                            <CardDescription className="text-sm mt-2 leading-relaxed">
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
                            <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                              <Label className="text-sm font-semibold text-green-900 flex items-center gap-1 mb-2">
                                <CheckCircle className="h-4 w-4" />
                                Correct Answer
                              </Label>
                              <p className="text-sm text-green-800">
                                {question.correct_answer}
                              </p>
                            </div>
                          )}

                          {question.sample_answer &&
                            question.sample_answer !== question.correct_answer && (
                              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                                <Label className="text-sm font-semibold text-blue-900 flex items-center gap-1 mb-2">
                                  <Target className="h-4 w-4" />
                                  Sample Answer
                                </Label>
                                <p className="text-sm text-blue-800">
                                  {question.sample_answer}
                                </p>
                              </div>
                            )}

                          {question.explanation && (
                            <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                              <Label className="text-sm font-semibold text-purple-900 flex items-center gap-1 mb-2">
                                <Lightbulb className="h-4 w-4" />
                                Explanation
                              </Label>
                              <p className="text-sm text-purple-800">
                                {question.explanation}
                              </p>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          ) : questions.length > 0 ? (
            <div className="text-center py-12 bg-gray-50 rounded-lg border animate-fade-in">
              <Filter className="h-12 w-12 text-gray-300 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No Questions Match Filters
              </h3>
              <p className="text-gray-500 mb-4">
                Try adjusting your search or filter criteria
              </p>
              <Button
                variant="outline"
                onClick={() => {
                  setSearchQuery("");
                  setDifficultyFilter("all");
                  setTypeFilter("all");
                }}
              >
                Clear Filters
              </Button>
            </div>
          ) : selectedExamId && !isLoading ? (
            <div className="text-center py-12 bg-gray-50 rounded-lg border">
              <FileText className="h-12 w-12 text-gray-300 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No Questions Found
              </h3>
              <p className="text-gray-500">
                This exam doesn't have any questions yet
              </p>
            </div>
          ) : null}
        </div>
      </CardContent>
    </Card>
  );
}