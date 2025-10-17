/**
 * TypeScript types for the exam system
 */

export type Document = {
  id: string | number;
  title?: string;
  filename?: string;
  uploaded_at?: string;
};

export type Exam = {
  id: string | number;
  title: string;
  status?: string;
  duration?: number;
  created_at?: string;
  document_id?: string | number;
  total_questions?: number;
  completed?: boolean;
};

export type Question = {
  id: string | number;
  type?: "mcq" | "short" | "numeric" | string;
  text?: string;
  question_text?: string;
  options?: string[];
  points?: number;
  correct_answer?: string;
  difficulty_level?: number;
};

export type UploadResponse = {
  success: boolean;
  doc_id: string | number;
  filename?: string;
  title?: string;
  grading_instructions?: string;
  result?: {
    level_3_questions: Question[];
    level_4_questions: Question[];
    level_5_questions: Question[];
    total_questions: number;
  };
};

export type CreateExamRequest = {
  title?: string;
  document_id: string | number;
  levels: number[];
  questions_per_level: number;
};

export type CreateExamResponse = {
  success: boolean;
  exam_id: string | number;
  questions?: number;
  message?: string;
};

export type StartExamResponse = {
  success: boolean;
  session_id: number;
  selected_questions?: Question[];
  total_questions?: number;
  message?: string;
};

export type QuestionsResponse = {
  success: boolean;
  exam_id: number;
  questions: Question[];
  total_questions?: number;
};

export type SubmitAnswersRequest = {
  exam_session_id: number;
  question_id: number;
  answer: string;
};

export type SubmitAnswersResponse = {
  success: boolean;
  is_correct: boolean;
  score?: number;
  max_score?: number;
  reasoning?: string;
  next_question?: Question;
  has_more_questions?: boolean;
};

export type FinishExamResponse = {
  success: boolean;
  exam_session_id: number;
  questions_answered?: number;
  total_questions_in_exam?: number;
  correct_answers?: number;
  total_score_earned?: number;
  max_possible_score?: number;
  percentage_of_exam_completed?: number;
  percentage_of_answered_correct?: number;
  points_per_question?: number;
  final_score?: number;
  summary?: string;
};

export type HealthResponse = {
  status: string;
  message?: string;
  [key: string]: unknown;
};

// UI-specific types
export type DocumentOption = {
  label: string;
  value: string | number;
  id: string | number;
};

export type ExamCard = {
  title: string;
  status: string;
  id: string | number;
  created_at?: string;
  total_questions?: number;
  completed?: boolean;
};

export type ExamRef = {
  id: string | number;
  title: string;
};

export type ApiError = {
  message: string;
  status: number;
};
