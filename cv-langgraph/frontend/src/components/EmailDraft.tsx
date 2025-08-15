"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import ReactMarkdown from "react-markdown";

interface EmailDraftProps {
  emailDraft: string;
  onSendMessage: (message: string) => void;
  onFetchCandidates: () => void;
  onFetchEmailDraft: () => void;
  onUpdateDraft?: (updatedDraft: string) => void; // New prop for updating draft
  isLoading?: boolean;
  sessionID: string;
}

export function EmailDraft({
  emailDraft,
  onSendMessage,
  onFetchCandidates,
  onFetchEmailDraft,
  onUpdateDraft, // New prop
  isLoading = false,
  sessionID,
}: EmailDraftProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editableDraft, setEditableDraft] = useState(emailDraft || "");

  // Update editableDraft when emailDraft changes
  useEffect(() => {
    setEditableDraft(emailDraft || "");
  }, [emailDraft]);

  const handleEdit = () => {
    setEditableDraft(emailDraft);
    setIsEditing(true);
  }; 

  const handleSaveChanges = () => {
    if (editableDraft.trim()) {
      // Update the draft instead of sending as message
      if (onUpdateDraft) {
        onUpdateDraft(editableDraft.trim());
      }
      setIsEditing(false);
    }
  };


  return (
    <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
      <CardHeader className="bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-t-lg">
        <CardTitle className="flex items-center text-xl">
          <span className="mr-3">📧</span>
          Generated Email Draft
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6">
        {emailDraft ? (
          <div className="bg-gradient-to-br from-gray-50 to-blue-50/30 p-6 rounded-xl mb-6 border border-gray-100 shadow-inner">
            <div className="prose prose-sm max-w-none">
              <div className="text-gray-800 leading-relaxed">
                {isEditing ? (
                  <Textarea
                    value={editableDraft}
                    onChange={(e) => setEditableDraft(e.target.value)}
                    rows={10}
                    className="w-full border border-blue-300 bg-white p-4 rounded-lg shadow-sm text-sm"
                  />
                ) : (
                  <ReactMarkdown
                    components={{
                      h1: ({ children }) => (
                        <h1 className="text-xl font-bold text-gray-900 mb-3">
                          {children}
                        </h1>
                      ),
                      h2: ({ children }) => (
                        <h2 className="text-lg font-semibold text-gray-800 mb-2">
                          {children}
                        </h2>
                      ),
                      p: ({ children }) => (
                        <p className="mb-3 text-gray-700">{children}</p>
                      ),
                      strong: ({ children }) => (
                        <strong className="font-semibold text-gray-900">
                          {children}
                        </strong>
                      ),
                    }}
                  >
                    {emailDraft}
                  </ReactMarkdown>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-gray-50 p-8 rounded-xl mb-6 text-center border-2 border-dashed border-gray-200">
            <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl text-gray-400">📝</span>
            </div>
            <p className="text-gray-500 text-lg">
              No email draft generated yet.
            </p>
            <p className="text-gray-400 text-sm mt-2">
              Start chatting to generate your campaign email!
            </p>
          </div>
        )}

        {/* API Endpoint Buttons */}
        <div className="mb-6">
          <div className="flex space-x-3">
            <Button
              onClick={onFetchCandidates}
              disabled={isLoading}
              variant="outline"
              className="flex-1 h-12 bg-white hover:bg-blue-50 border-blue-200 text-blue-700 hover:border-blue-300 rounded-xl transition-all duration-200 hover:shadow-md"
            >
              {isLoading ? (
                <div className="flex items-center">
                  <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mr-2"></div>
                  Loading...
                </div>
              ) : (
                <>
                  <span className="mr-2">👥</span>
                  Fetch Candidates
                </>
              )}
            </Button>
            <Button
              onClick={onFetchEmailDraft}
              disabled={isLoading}
              variant="outline"
              className="flex-1 h-12 bg-white hover:bg-green-50 border-green-200 text-green-700 hover:border-green-300 rounded-xl transition-all duration-200 hover:shadow-md"
            >
              {isLoading ? (
                <div className="flex items-center">
                  <div className="w-4 h-4 border-2 border-green-600 border-t-transparent rounded-full animate-spin mr-2"></div>
                  Loading...
                </div>
              ) : (
                <>
                  <span className="mr-2">🔄</span>
                  Refresh Draft
                </>
              )}
            </Button>
          </div>
        </div>
        {isEditing ? (
          <div className="flex space-x-3">
            <Button
              onClick={handleSaveChanges}
              disabled={!editableDraft.trim()}
              className="bg-green-600 hover:bg-green-700 text-white rounded-lg shadow-md hover:shadow-lg transition-all duration-200"
            >
              <span className="mr-2">💾</span>
              Save Changes
            </Button>
            
            <Button
              variant="outline"
              onClick={() => setIsEditing(false)}
              className="border-gray-300 hover:bg-gray-50 rounded-lg"
            >
              Cancel
            </Button>
          </div>
        ) : (
        <div className="flex space-x-3">
  <Button
    variant="outline"
    onClick={handleEdit}
    disabled={!emailDraft}
    className="flex-1 h-12 border-gray-300 hover:bg-gray-50 rounded-xl transition-all duration-200 hover:shadow-md"
  >
    <span className="mr-2">✏️</span>
    Edit Draft
  </Button>
  <Button
  onClick={async () => {
    const draftToSend = isEditing ? editableDraft.trim() : emailDraft.trim();
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/send_email?session_id=${sessionID}`, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email_with_candidates: {
            email_draft: draftToSend,
          },
        }),
      });

      if (response.ok) {
        alert("✅ Email draft sent successfully!");
      } else {
        const errorData = await response.json();
        alert(`❌ Failed to send draft: ${errorData.detail || response.statusText}`);
      }
    } catch (error) {
      alert(`❌ Network error: ${error}`);
    }
  }}
  disabled={!emailDraft.trim()}
  className="flex-1 h-12 bg-blue-600 hover:bg-blue-700 text-white rounded-xl shadow-md hover:shadow-lg transition-all duration-200"
>
  <span className="mr-2">📨</span>
  Send Draft
</Button>

</div>

        )}
      </CardContent>
    </Card>
  );
}
