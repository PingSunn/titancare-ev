/**
 * Hook for managing chat sessions with localStorage persistence
 */

import { useState, useCallback, useEffect } from "react";
import type { Session, Message } from "@/types";

const STORAGE_KEY = "titancare_sessions";

interface UseSessionsReturn {
  sessions: Session[];
  activeSessionId: string | null;
  activeSession: Session | null;
  createSession: () => Session;
  selectSession: (id: string) => void;
  deleteSession: (id: string) => void;
  updateSessionMessages: (sessionId: string, messages: Message[]) => void;
  updateSessionTitle: (sessionId: string, title: string) => void;
}

function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function generateTitle(messages: Message[]): string {
  if (messages.length === 0) return "New Chat";

  const firstUserMessage = messages.find((m) => m.role === "user");
  if (!firstUserMessage) return "New Chat";

  // Truncate to first 30 characters
  const title = firstUserMessage.content.slice(0, 30);
  return title.length < firstUserMessage.content.length ? `${title}...` : title;
}

function loadSessions(): Session[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];

    const sessions = JSON.parse(stored) as Session[];
    // Convert date strings back to Date objects
    return sessions.map((s) => ({
      ...s,
      createdAt: new Date(s.createdAt),
      updatedAt: new Date(s.updatedAt),
      messages: s.messages.map((m) => ({
        ...m,
        timestamp: new Date(m.timestamp),
      })),
    }));
  } catch {
    return [];
  }
}

function saveSessions(sessions: Session[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
  } catch {
    console.error("Failed to save sessions to localStorage");
  }
}

export function useSessions(): UseSessionsReturn {
  const [sessions, setSessions] = useState<Session[]>(() => loadSessions());
  const [activeSessionId, setActiveSessionId] = useState<string | null>(() => {
    const loaded = loadSessions();
    return loaded.length > 0 ? loaded[0].id : null;
  });

  // Save to localStorage whenever sessions change
  useEffect(() => {
    saveSessions(sessions);
  }, [sessions]);

  const activeSession =
    sessions.find((s) => s.id === activeSessionId) ?? null;

  const createSession = useCallback((): Session => {
    const now = new Date();
    const newSession: Session = {
      id: generateSessionId(),
      title: "New Chat",
      messages: [],
      createdAt: now,
      updatedAt: now,
    };

    setSessions((prev) => [newSession, ...prev]);
    setActiveSessionId(newSession.id);

    return newSession;
  }, []);

  const selectSession = useCallback((id: string) => {
    setActiveSessionId(id);
  }, []);

  const deleteSession = useCallback(
    (id: string) => {
      setSessions((prev) => {
        const filtered = prev.filter((s) => s.id !== id);

        // If deleting active session, select the first remaining one
        if (id === activeSessionId) {
          setActiveSessionId(filtered.length > 0 ? filtered[0].id : null);
        }

        return filtered;
      });
    },
    [activeSessionId]
  );

  const updateSessionMessages = useCallback(
    (sessionId: string, messages: Message[]) => {
      setSessions((prev) =>
        prev.map((s) => {
          if (s.id !== sessionId) return s;

          // Auto-generate title from first user message
          const newTitle =
            s.title === "New Chat" ? generateTitle(messages) : s.title;

          return {
            ...s,
            messages,
            title: newTitle,
            updatedAt: new Date(),
          };
        })
      );
    },
    []
  );

  const updateSessionTitle = useCallback(
    (sessionId: string, title: string) => {
      setSessions((prev) =>
        prev.map((s) =>
          s.id === sessionId ? { ...s, title, updatedAt: new Date() } : s
        )
      );
    },
    []
  );

  return {
    sessions,
    activeSessionId,
    activeSession,
    createSession,
    selectSession,
    deleteSession,
    updateSessionMessages,
    updateSessionTitle,
  };
}
