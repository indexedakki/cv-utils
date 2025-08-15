'use client';

import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CandidatesResponse } from '@/types';
import axios from 'axios';

interface CandidatesListProps {
  candidatesData: CandidatesResponse | null;
  onRefresh: () => void;
  sessionId: string;
}

export function CandidatesList({ candidatesData, onRefresh, sessionId }: CandidatesListProps) {
  const [selectedEmails, setSelectedEmails] = useState<string[]>([]);

  if (!candidatesData || !candidatesData.candidates) {
    return (
      <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
        <CardHeader className="bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-t-lg">
          <CardTitle className="flex items-center text-xl">
            <span className="mr-3">👥</span>
            Candidates
          </CardTitle>
        </CardHeader>
        <CardContent className="p-8 text-center">
          <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <span className="text-3xl text-gray-400">🔍</span>
          </div>
          <h3 className="text-lg font-semibold text-gray-800 mb-3">No candidates found</h3>
          <p className="text-gray-600 mb-6">Click &quot;Fetch Candidates&quot; to load candidate data.</p>
          <Button 
            onClick={onRefresh} 
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-0.5"
          >
            <span className="mr-2">🔄</span>
            Fetch Candidates
          </Button>
        </CardContent>
      </Card>
    );
  }

  const { candidates } = candidatesData;
  const candidateCount = candidates.name?.length || 0;

  const toggleEmailSelection = (email: string) => {
    setSelectedEmails(prev =>
      prev.includes(email) ? prev.filter(e => e !== email) : [...prev, email]
    );
  };

  const handleSubmit = async () => {
    try {
      await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/send_email?session_id=${sessionId}`, {
        email_with_candidates: {
        emails: selectedEmails
      }
      });
      alert('Selected emails submitted successfully!');
    } catch (err) {
      console.error('Submit failed:', err);
      alert('Failed to submit emails.');
    }
  };

  return (
    <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-t-lg">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center text-xl">
            <span className="mr-3">👥</span>
            Candidates ({candidateCount})
          </CardTitle>
          <Button 
            onClick={onRefresh} 
            variant="outline" 
            size="sm"
            className="bg-white/20 border-white/30 text-white hover:bg-white/30 rounded-lg"
          >
            <span className="mr-1">🔄</span>
            Refresh
          </Button>
        </div>
      </CardHeader>

      <CardContent className="p-6">
        <div className="space-y-4">
          {candidates.name?.map((name, index) => {
            const email = candidates.email?.[index] || '';
            return (
              <div key={index} className="group">
                <div className="bg-gradient-to-br from-gray-50 to-blue-50/30 border border-gray-200 rounded-xl p-5 transition-all duration-200 hover:shadow-lg hover:border-blue-200 hover:-translate-y-0.5">
                  <div className="flex justify-between items-start mb-4">
                    <h4 className="font-semibold text-lg text-gray-900 flex items-center">
                      <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-sm mr-3">
                        {name.charAt(0).toUpperCase()}
                      </div>
                      {name}
                    </h4>
                    <div className="flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                      <span className="mr-1">⭐</span>
                      {candidates.experience?.[index] || 'N/A'} years
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center text-gray-600">
                      <span className="mr-3 text-lg">📧</span>
                      <span className="text-sm font-medium">{email}</span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <span className="mr-3 text-lg">📍</span>
                      <span className="text-sm font-medium">
                        {candidates.location?.[index] || 'Location not specified'}
                      </span>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-gray-200 flex justify-between items-center">
                    <div className="flex items-center text-xs text-gray-500">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                      Available for contact
                    </div>
                    <Button
                      variant={selectedEmails.includes(email) ? 'secondary' : 'outline'}
                      size="sm"
                      className="rounded-md bg-blue-500 hover:bg-green-500 text-white"
                      onClick={() => toggleEmailSelection(email)}
                    >
                      {selectedEmails.includes(email) ? 'Selected' : 'Select'}
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {selectedEmails.length > 0 && (
          <div className="pt-6 text-center">
            <Button
              onClick={handleSubmit}
              className="bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 text-white px-6 py-2 rounded-xl shadow-md"
            >
              🚀 Submit Selected ({selectedEmails.length})
            </Button>
          </div>
        )}

        {candidateCount === 0 && (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl text-gray-400">👤</span>
            </div>
            <p className="text-gray-500">No candidates to display</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
