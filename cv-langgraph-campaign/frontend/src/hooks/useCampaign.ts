'use client';

import { useState, useCallback, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import { generateSessionId } from '@/lib/utils';
import { 
  CampaignRequest, 
  CampaignResponse, 
  ChatMessage, 
  CandidatesResponse,
  EmailDraftResponse
} from '@/types';

export function useCampaign() {
  const [sessionId, setSessionId] = useState<string>('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [emailDraft, setEmailDraft] = useState<string>('');
  const [candidatesData, setCandidatesData] = useState<CandidatesResponse | null>(null);
  const [emailDraftData, setEmailDraftData] = useState<EmailDraftResponse | null>(null);
  const [error, setError] = useState<string>('');
  
  useEffect(() => {
    const newSessionId = generateSessionId();
    setSessionId(newSessionId);
  }, []);

  const addMessage = useCallback((text: string, isUser: boolean) => {
    const newMessage: ChatMessage = {
      id: `msg_${Date.now()}`,
      text,
      isUser,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);
  }, []);

  const sendMessage = useCallback(async (userInput: string) => {
    if (!userInput.trim() || !sessionId) return;

    setIsLoading(true);
    setError('');
    
    
    addMessage(userInput, true);

    try {
      const request: CampaignRequest = {
        user_input: userInput,
        session_id: sessionId,
        validation: false,
      };

      const response = await apiClient.sendCampaignMessage(request);
      
      
      if (response.message) {
        addMessage(response.message, false);
      }
      
      if (response.email_draft) {
        setEmailDraft(response.email_draft);
        addMessage('Email draft has been generated! You can view it now.', false);
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Something went wrong';
      setError(errorMessage);
      addMessage('Sorry, there was an error processing your request.', false);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, addMessage]);

  const fetchCandidates = useCallback(async () => {
    if (!sessionId) return;

    try {
      const response = await apiClient.getCandidates(sessionId);
      setCandidatesData(response);
    } catch (err) {
      console.error('Failed to fetch candidates:', err);
    }
  }, [sessionId]);

  const fetchEmailDraft = useCallback(async () => {
    if (!sessionId) return;

    try {
      const response = await apiClient.getEmailDraft(sessionId);
      setEmailDraft(response.candidates); 
      setEmailDraftData(response); 
    } catch (err) {
      console.error('Failed to fetch email draft:', err);
    }
  }, [sessionId]);

  
  const updateEmailDraft = useCallback((updatedDraft: string) => {
    setEmailDraft(updatedDraft);
    addMessage('Email draft has been updated!', false);
  }, [addMessage]);

  return {
    sessionId,
    messages,
    isLoading,
    emailDraft,
    candidatesData,
    emailDraftData,
    error,
    sendMessage,
    fetchCandidates,
    fetchEmailDraft,
    updateEmailDraft,
  };
}