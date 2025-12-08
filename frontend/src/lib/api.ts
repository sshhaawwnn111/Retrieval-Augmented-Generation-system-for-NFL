const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface LLMGenerateRequest {
  prompt: string;
  system_prompt?: string;
  max_tokens?: number;
  temperature?: number;
  top_p?: number;
  stop_sequences?: string[];
}

interface LLMGenerateResponse {
  generated_text: string;
  model: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

interface Text2SQLRequest {
  question: string;
  schema_context?: string;
  few_shot_examples?: Array<{ question: string; sql: string }>;
}

interface Text2SQLResponse {
  sql: string;
  explanation?: string;
}

interface ReportGenerationRequest {
  query_results: Record<string, any>;
  report_type?: string;
  additional_context?: string;
}

interface ReportGenerationResponse {
  report: string;
  report_type: string;
}

interface HealthCheckResponse {
  status: string;
  message: string;
}

class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck(): Promise<HealthCheckResponse> {
    return this.request<HealthCheckResponse>('/health');
  }

  // Generate text
  async generateText(data: LLMGenerateRequest): Promise<LLMGenerateResponse> {
    return this.request<LLMGenerateResponse>('/api/v1/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Text to SQL
  async textToSQL(data: Text2SQLRequest): Promise<Text2SQLResponse> {
    return this.request<Text2SQLResponse>('/api/v1/text2sql', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Retrieve context
  async retrieveContext(query: string, topK: number = 5) {
    return this.request('/api/v1/retrieve', {
      method: 'POST',
      body: JSON.stringify({ query, top_k: topK }),
    });
  }

  // Generate report
  async generateReport(data: ReportGenerationRequest): Promise<ReportGenerationResponse> {
    return this.request<ReportGenerationResponse>('/api/v1/generate-report', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export const apiClient = new APIClient();
export default apiClient;
