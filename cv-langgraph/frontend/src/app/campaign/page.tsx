'use client';

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { ChatInterface } from '@/components/ChatInterface';
import { EmailDraft } from '@/components/EmailDraft';
import { CandidatesList } from '@/components/CandidatesList';
import { useCampaign } from '@/hooks/useCampaign';

export default function CampaignPage() {
  const {
    sessionId,
    messages,
    isLoading,
    emailDraft,
    candidatesData,
    error,
    sendMessage,
    fetchCandidates,
    fetchEmailDraft,
    updateEmailDraft, 
  } = useCampaign();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Campaign Generator
          </h1>
          <p className="text-gray-600">
            Create your recruitment campaign by chatting with our AI assistant
          </p>
          {sessionId && (
            <p className="text-sm text-gray-500 mt-2">
              Session ID: {sessionId}
            </p>
          )}
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md">
            Error: {error}
          </div>
        )}

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Chat Interface */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle style={{color: "black"}}>Chat with AI Assistant</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <ChatInterface
                  messages={messages}
                  isLoading={isLoading}
                  onSendMessage={sendMessage}
                />
              </CardContent>
            </Card>
          </div>

          <div>
            <EmailDraft 
              emailDraft={emailDraft}
              onSendMessage={sendMessage}
              onFetchCandidates={fetchCandidates}
              onFetchEmailDraft={fetchEmailDraft}
              onUpdateDraft={updateEmailDraft} 
              isLoading={isLoading}
              sessionID={sessionId}
            />
            
            <CandidatesList 
              candidatesData={candidatesData}
              onRefresh={fetchCandidates}
              sessionId={sessionId}
            />
          </div>
        </div>
      </div>
    </div>
  );
}