import { API_BASE_URL, API_ENDPOINTS } from '@/app/api/config';
import { 
  CampaignRequest, 
  CampaignResponse, 
  CandidatesResponse, 
  EmailDraftResponse 
} from '@/types';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  async sendCampaignMessage(data: CampaignRequest): Promise<CampaignResponse> {
    return this.request<CampaignResponse>(API_ENDPOINTS.CAMPAIGN, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getCandidates(sessionId: string): Promise<CandidatesResponse> {
    return this.request<CandidatesResponse>(
      `${API_ENDPOINTS.CANDIDATES}?session_id=${sessionId}`
    );
  }

  async getEmailDraft(sessionId: string): Promise<EmailDraftResponse> {
    return this.request<EmailDraftResponse>(
      `${API_ENDPOINTS.EMAIL_DRAFT}?session_id=${sessionId}`
    );
  }
}

export const apiClient = new ApiClient(API_BASE_URL || 'http://127.0.0.1:8000');