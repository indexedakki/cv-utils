'use client';

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { CandidatesResponse, EmailDraftResponse } from '@/types';

interface ResponseDisplayProps {
  candidatesData: CandidatesResponse | null;
  emailDraftData: EmailDraftResponse | null;
}

export function ResponseDisplay({ candidatesData, emailDraftData }: ResponseDisplayProps) {
  return (
    <div className="space-y-6">
      {/* Candidates Response */}
      {candidatesData && (
        <Card>
          <CardHeader>
            <CardTitle>API Response: /candidates</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-50 p-4 rounded-md">
              <pre className="text-sm overflow-x-auto">
                {JSON.stringify(candidatesData, null, 2)}
              </pre>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Email Draft Response */}
      {emailDraftData && (
        <Card>
          <CardHeader>
            <CardTitle>API Response: /email_draft</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-50 p-4 rounded-md">
              <pre className="text-sm overflow-x-auto">
                {JSON.stringify(emailDraftData, null, 2)}
              </pre>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 