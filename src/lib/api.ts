// Tipos para as respostas da API
export interface EmailAnalysisResult {
  classification: "Productive" | "Non-Productive";
  confidence: number;
  suggested_response: string;
  original_text: string;
  processed_text: string;
  ai_method: string;
  sentiment_analysis: Record<string, number>;
  analysis: {
    text_length: number;
    word_count: number;
    processed_words: number;
    question_marks: number;
    exclamation_marks: number;
    device_used: string;
  };
  model_info: {
    sentiment_model_loaded: boolean;
    text_classifier_loaded: boolean;
    torch_version: string;
  };
}

export interface ApiError {
  error: string;
}

export interface HealthStatus {
  status: string;
  service: string;
  version: string;
  ai_models?: {
    sentiment_model: boolean;
    text_classifier: boolean;
    device: string;
    torch_version: string;
  };
  features?: string[];
}

export interface EmailExamples {
  productive: string[];
  non_productive: string[];
}

// Configuração da API
const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  "http://localhost:5000/api";

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  private async handleResponse<T>(
    response: Response
  ): Promise<T> {
    if (!response.ok) {
      const errorData = await response
        .json()
        .catch(() => ({ error: "Unknown error occurred" }));
      throw new Error(
        errorData.error ||
          `HTTP ${response.status}: ${response.statusText}`
      );
    }

    return response.json();
  }

  async analyzeEmail(
    formData: FormData
  ): Promise<EmailAnalysisResult> {
    try {
      const response = await fetch(
        `${this.baseUrl}/analyze`,
        {
          method: "POST",
          body: formData,
        }
      );

      return this.handleResponse<EmailAnalysisResult>(
        response
      );
    } catch (error) {
      throw error instanceof Error
        ? error
        : new Error("Failed to analyze email");
    }
  }

  async analyzeEmailText(
    text: string
  ): Promise<EmailAnalysisResult> {
    const formData = new FormData();
    formData.append("text", text);

    return this.analyzeEmail(formData);
  }

  async analyzeEmailFile(
    file: File
  ): Promise<EmailAnalysisResult> {
    const formData = new FormData();
    formData.append("file", file);

    return this.analyzeEmail(formData);
  }

  async healthCheck(): Promise<HealthStatus> {
    try {
      const response = await fetch(
        `${this.baseUrl}/health`
      );
      return this.handleResponse<HealthStatus>(response);
    } catch (error) {
      throw error instanceof Error
        ? error
        : new Error("Health check failed");
    }
  }

  async getExamples(): Promise<EmailExamples> {
    try {
      const response = await fetch(
        `${this.baseUrl}/examples`
      );
      return this.handleResponse<EmailExamples>(response);
    } catch (error) {
      throw error instanceof Error
        ? error
        : new Error("Failed to fetch examples");
    }
  }

  isValidFile(file: File): boolean {
    const allowedTypes = ["text/plain", "application/pdf"];
    const maxSize = 16 * 1024 * 1024; // 16MB

    if (!allowedTypes.includes(file.type)) {
      throw new Error(
        "Invalid file type. Please upload .txt or .pdf files only."
      );
    }

    if (file.size > maxSize) {
      throw new Error(
        "File too large. Maximum size is 16MB."
      );
    }

    return true;
  }
}

// Instância singleton da API
export const apiService = new ApiService();

// Hook personalizado para usar com React Query ou SWR
export const useEmailAnalysis = () => {
  return {
    analyzeText: (text: string) =>
      apiService.analyzeEmailText(text),
    analyzeFile: (file: File) => {
      apiService.isValidFile(file);
      return apiService.analyzeEmailFile(file);
    },
    healthCheck: () => apiService.healthCheck(),
    getExamples: () => apiService.getExamples(),
  };
};

export default apiService;
