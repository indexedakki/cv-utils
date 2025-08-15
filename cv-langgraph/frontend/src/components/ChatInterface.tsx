'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { ChatMessage } from '@/types';

interface ChatInterfaceProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSendMessage: (message: string) => void;
}

export function ChatInterface({ messages, isLoading, onSendMessage }: ChatInterfaceProps) {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  return (
    <div className="flex flex-col h-[600px]">
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-gray-50/50 to-white">
        {messages.length === 0 ? (
          <div className="text-center mt-20">
            <div className="w-20 h-20 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-3xl">💬</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-800 mb-3">Start a conversation</h3>
            <p className="text-gray-600 mb-4">Generate your campaign by describing your requirements!</p>
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 max-w-md mx-auto">
              <p className="text-sm text-blue-800 font-medium mb-2">💡 Try this example:</p>
              <p className="text-sm text-blue-700 italic">
                &quot;I want to generate a campaign for a Python Developer with 3+ years of experience for location Bangalore&quot;
              </p>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}
            >
              <div className={`max-w-[85%] ${message.isUser ? 'order-2' : 'order-1'}`}>
                <Card className={`shadow-lg border-0 ${
                  message.isUser 
                    ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white transform hover:scale-[1.02] transition-transform duration-200' 
                    : 'bg-white border border-gray-100'
                }`}>
                  <CardContent className="p-4">
                    <div className="flex items-start space-x-3">
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                        message.isUser 
                          ? 'bg-white/20 text-white' 
                          : 'bg-gradient-to-r from-purple-500 to-purple-600 text-white'
                      }`}>
                        {message.isUser ? '👤' : '🤖'}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm leading-relaxed whitespace-pre-wrap ${
                          message.isUser ? 'text-white' : 'text-gray-800'
                        }`}>
                          {message.text}
                        </p>
                        <p className={`text-xs mt-2 ${
                          message.isUser ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start animate-fade-in">
            <Card className="bg-white border border-gray-100 shadow-lg">
              <CardContent className="p-4">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-purple-600 rounded-full flex items-center justify-center text-sm">
                    🤖
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <p className="text-sm text-gray-600 ml-2">AI is thinking...</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>

     
      <div className="border-t border-gray-200 bg-white p-4">
        <form onSubmit={handleSubmit} className="flex space-x-3">
          <div className="flex-1 relative">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type your message..."
              disabled={isLoading}
              className="pr-12 h-12 rounded-xl border-gray-200 focus:border-blue-500 focus:ring-blue-500 bg-gray-50 focus:bg-white transition-colors text-black"
            />
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
              <span className="text-gray-400 text-sm">💬</span>
            </div>
          </div>
          <Button 
            type="submit" 
            disabled={isLoading || !inputValue.trim()}
            className="h-12 px-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-0.5"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <>
                Send
                <span className="ml-2">→</span>
              </>
            )}
          </Button>
        </form>
      </div>
    </div>
  );
}