import { schemaRegistry } from "./schemaRegistry";
import type {
  Document,
  Exam,
  UploadResponse,
  CreateExamRequest,
  CreateExamResponse,
  StartExamResponse,
  QuestionsResponse,
  SubmitAnswersRequest,
  SubmitAnswersResponse,
  FinishExamResponse,
  HealthResponse,
  DocumentOption,
  ExamCard,
} from "./types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "";

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async fetchJson<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    const defaultHeaders: HeadersInit = {
      "Content-Type": "application/json",
    };

    // Don't set Content-Type for FormData (multipart)
    if (options.body instanceof FormData) {
      delete defaultHeaders["Content-Type"];
    }

    const response = await fetch(url, {
      ...options,
      credentials: "include",
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    });

    if (!response.ok) {
      // Handle auth errors
      if (response.status === 401 || response.status === 403) {
        localStorage.removeItem("auth");
        window.location.href = "/signin";
        throw new ApiError("Authentication required", response.status);
      }

      let errorMessage = `HTTP ${response.status}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.error || errorData.detail || errorMessage;
      } catch {
        // Use default error message if JSON parsing fails
      }

      throw new ApiError(errorMessage, response.status);
    }

    // Handle empty responses
    const text = await response.text();
    if (!text) {
      return {} as T;
    }

    try {
      return JSON.parse(text);
    } catch {
      throw new ApiError("Invalid JSON response", response.status);
    }
  }

  // Health check
  async getHealth(): Promise<HealthResponse> {
    return this.fetchJson<HealthResponse>("/api/health/");
  }

  // Document APIs
  async uploadDocument(
    file: File,
    gradingInstructions?: string
  ): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    // Add grading instructions if provided
    if (gradingInstructions) {
      formData.append("grading_instructions", gradingInstructions);
    }

    const response = await this.fetchJson<UploadResponse>(
      "/api/documents/upload/",
      {
        method: "POST",
        body: formData,
      }
    );


    // Store in session uploads for fallback
    if (response.success && response.doc_id) {
      const label = response.filename || response.title || file.name;
      console.log("Adding to session uploads:", {
        label,
        document_id: response.doc_id,
      });
      schemaRegistry.addSessionUpload(label, response.doc_id);
      console.log(
        "Session uploads after add:",
        schemaRegistry.getSessionUploads()
      );
    } else {
      console.log("Upload response missing success or doc_id:", response);
    }

    return response;
  }

  async listDocuments(): Promise<DocumentOption[]> {
    // Since there's no documents list endpoint, rely on session uploads
    const sessionUploads = schemaRegistry.getSessionUploads();

    console.log("Session uploads:", sessionUploads);

    if (sessionUploads.length === 0) {
      console.log("No session uploads found");
      return [];
    }

    return sessionUploads.map((upload) => ({
      label: upload.label,
      value: upload.document_id,
      id: upload.document_id,
    }));
  }

  // Exam APIs
  async createExam(payload: CreateExamRequest): Promise<CreateExamResponse> {
    const response = await this.fetchJson<CreateExamResponse>(
      "/api/exams/create/",
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );

    // Store in session exams
    if (response.success && response.exam_id) {
      schemaRegistry.addSessionExam(payload.title, response.exam_id);
    }

    return response;
  }

  async listExamsForStudent(): Promise<ExamCard[]> {
    try {
      // Try to get exams from the actual API first
      const response = await this.fetchJson<{ success: boolean; exams: any[] }>(
        "/api/exams/"
      );

      if (response.success && response.exams) {
        return response.exams.map((exam: any) => ({
          title: exam.title || `Exam ${exam.id}`,
          status: "Available",
          id: exam.id,
          created_at: exam.created_at,
          total_questions: exam.total_questions || 10,
        }));
      }
    } catch (error) {
      console.log("API call failed, falling back to session exams:", error);
    }

    // Fallback: try session exams (created in this session)
    const sessionExams = schemaRegistry.getSessionExams();

    if (sessionExams.length > 0) {
      return sessionExams.map((exam) => ({
        title: exam.title,
        status: "Available",
        id: exam.exam_id,
        created_at: exam.created_at,
        total_questions: 10, // We know it's always 10 questions
      }));
    }

    // Fallback: check for examId in URL
    const urlParams = new URLSearchParams(window.location.search);
    const examId = urlParams.get("examId");

    if (examId) {
      return [
        {
          title: "Shared Exam",
          status: "Available",
          id: examId,
          created_at: new Date().toISOString(),
          total_questions: 10,
        },
      ];
    }

    return [];
  }

  async startExam(
    examId: string | number,
    studentId: number
  ): Promise<StartExamResponse> {
    return this.fetchJson<StartExamResponse>(`/api/exams/${examId}/start/`, {
      method: "POST",
      body: JSON.stringify({ student_id: studentId }),
    });
  }

  async getQuestions(examId: string | number): Promise<QuestionsResponse> {
    return this.fetchJson<QuestionsResponse>(`/api/exams/${examId}/questions/`);
  }

  async submitAnswers(
    examId: string | number,
    payload: SubmitAnswersRequest
  ): Promise<SubmitAnswersResponse> {
    return this.fetchJson<SubmitAnswersResponse>(
      `/api/exams/${examId}/submit/`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
  }

  async finishExam(
    examId: string | number,
    examSessionId: number
  ): Promise<FinishExamResponse> {
    return this.fetchJson<FinishExamResponse>(`/api/exams/${examId}/finish/`, {
      method: "POST",
      body: JSON.stringify({ exam_session_id: examSessionId }),
    });
  }

  // Schema discovery
  async discoverEndpoints(): Promise<{
    documents: boolean;
    exams: boolean;
    hasAny: boolean;
  }> {
    await schemaRegistry.loadSchema();
    return schemaRegistry.getDiscoveryStatus();
  }
}

class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export const api = new ApiClient(API_BASE_URL);
export { ApiError };
