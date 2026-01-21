/**
 * Hook for managing chat state and interactions
 */

import { useState, useCallback } from "react";
import type { Message } from "@/types";
import { sendMessage as apiSendMessage } from "@/services/api";

interface UseChatOptions {
  sessionId?: string;
  model?: string;
  onSessionCreated?: (sessionId: string) => void;
}

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
  setMessages: (messages: Message[]) => void;
}

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const { sessionId, model, onSessionCreated } = options;

  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      setError(null);

      // Add user message immediately
      const userMessage: Message = {
        id: generateId(),
        role: "user",
        content: content.trim(),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      try {
        const response = await apiSendMessage(content, sessionId, model);

        // Notify about session creation
        if (response.session_id && onSessionCreated) {
          onSessionCreated(response.session_id);
        }

        // Add assistant message
        const assistantMessage: Message = {
          id: generateId(),
          role: "assistant",
          content: response.response,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to send message";
        setError(errorMessage);

        // Add error message as assistant response
        const errorResponse: Message = {
          id: generateId(),
          role: "assistant",
          content: `Error: ${errorMessage}`,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, errorResponse]);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId, model, isLoading, onSessionCreated]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    setMessages,
  };
}
