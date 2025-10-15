/**
 * React Query hooks for data fetching and caching
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "./api";
import type {
  DocumentOption,
  ExamCard,
  CreateExamRequest,
  SubmitAnswersRequest,
} from "./types";

// Query keys
export const queryKeys = {
  health: ["health"] as const,
  documents: ["documents"] as const,
  exams: ["exams"] as const,
  questions: (examId: string | number) => ["questions", examId] as const,
  discovery: ["discovery"] as const,
};

// Health check
export function useHealth() {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: () => api.getHealth(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Document queries
export function useDocuments() {
  return useQuery({
    queryKey: queryKeys.documents,
    queryFn: () => api.listDocuments(),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      file,
      gradingInstructions,
    }: {
      file: File;
      gradingInstructions?: string;
    }) => api.uploadDocument(file, gradingInstructions),
    onSuccess: () => {
      // Invalidate documents query to refresh the list
      queryClient.invalidateQueries({ queryKey: queryKeys.documents });
    },
  });
}

// Exam queries
export function useStudentExams() {
  return useQuery({
    queryKey: queryKeys.exams,
    queryFn: () => api.listExamsForStudent(),
    staleTime: 1 * 60 * 1000, // 1 minute
  });
}

export function useCreateExam() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateExamRequest) => api.createExam(payload),
    onSuccess: () => {
      // Invalidate exams query to refresh the list
      queryClient.invalidateQueries({ queryKey: queryKeys.exams });
    },
  });
}

export function useStartExam() {
  return useMutation({
    mutationFn: ({
      examId,
      studentId,
    }: {
      examId: string | number;
      studentId: number;
    }) => api.startExam(examId, studentId),
  });
}

export function useQuestions(examId: string | number) {
  return useQuery({
    queryKey: queryKeys.questions(examId),
    queryFn: () => api.getQuestions(examId),
    enabled: !!examId,
  });
}

export function useSubmitAnswers() {
  return useMutation({
    mutationFn: ({
      examId,
      payload,
    }: {
      examId: string | number;
      payload: SubmitAnswersRequest;
    }) => api.submitAnswers(examId, payload),
  });
}

export function useFinishExam() {
  return useMutation({
    mutationFn: ({
      examId,
      examSessionId,
    }: {
      examId: string | number;
      examSessionId: number;
    }) => api.finishExam(examId, examSessionId),
  });
}

// Discovery queries
export function useDiscovery() {
  return useQuery({
    queryKey: queryKeys.discovery,
    queryFn: () => api.discoverEndpoints(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Utility hooks
export function useExamRunner(examId: string | number) {
  const startExam = useStartExam();
  const questions = useQuestions(examId);
  const submitAnswers = useSubmitAnswers();
  const finishExam = useFinishExam();

  return {
    startExam,
    questions,
    submitAnswers,
    finishExam,
    isLoading:
      startExam.isPending ||
      questions.isLoading ||
      submitAnswers.isPending ||
      finishExam.isPending,
    error:
      startExam.error ||
      questions.error ||
      submitAnswers.error ||
      finishExam.error,
  };
}
