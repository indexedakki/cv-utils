export interface CampaignRequest {
  user_input: string;
  session_id?: string;
  validation?: boolean;
}

export interface CampaignResponse {
  message?: string;
  email_draft?: string;
}

export interface Candidate {
  id: string;
  name: string;
  email: string;
  skills: string[];
  experience: number;
  location: string;
}

// Updated to match actual API response structure
export interface CandidatesData {
  name: string[];
  email: string[];
  location: string[];
  experience: string[];
}

export interface CandidatesResponse {
  session_id: string;
  candidates: CandidatesData;
}

export interface EmailDraftResponse {
  session_id: string;
  candidates: string; // This is actually the email draft content
}

export interface ChatMessage {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}