import { useState, useCallback } from 'react';
import { apiClient } from '../api-client';
import type { Message, ChatHistoryItem } from '@/types';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (text: string, sourceIds?: string[]) => {
      const userMsg: Message = {
        id: crypto.randomUUID(),
        role: 'user',
        content: text,
        timestamp: new Date(),
      };

      const history: ChatHistoryItem[] = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);
      setError(null);

      try {
        const response = await apiClient.sendMessage(
          text,
          sourceIds,
          history,
        );

        const assistantMsg: Message = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: response.answer || 'Không có câu trả lời',
          timestamp: new Date(),
          sources: response.sources || [],
        };

        setMessages((prev) => [...prev, assistantMsg]);
      } catch (err) {
        const errorMsg =
          err instanceof Error ? err.message : 'Lỗi không xác định';
        setError(errorMsg);
        console.error('Chat error:', err);

        const errorAssistantMsg: Message = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: `⚠️ Xin lỗi, đã xảy ra lỗi: ${errorMsg}`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorAssistantMsg]);
      } finally {
        setIsLoading(false);
      }
    },
    [messages],
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    sendMessage,
    isLoading,
    error,
    clearMessages,
  };
}