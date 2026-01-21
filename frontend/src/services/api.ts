/**
 * API client for backend communication
 */

import type {
  ChatRequest,
  ChatResponse,
  SessionResponse,
  ModelsResponse,
  HealthResponse,
} from "@/types";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;

  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error.detail || "Request failed");
  }

  return response.json();
}

/**
 * Send a chat message to the backend
 */
export async function sendMessage(
  message: string,
  sessionId?: string,
  model?: string
): Promise<ChatResponse> {
  const payload: ChatRequest = {
    message,
    session_id: sessionId,
    model,
  };

  return request<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/**
 * Create a new chat session
 */
export async function createSession(userId?: string): Promise<SessionResponse> {
  const params = userId ? `?user_id=${encodeURIComponent(userId)}` : "";
  return request<SessionResponse>(`/session${params}`, {
    method: "POST",
  });
}

/**
 * Clear a session's history
 */
export async function clearSession(sessionId: string): Promise<void> {
  await request(`/session/${sessionId}`, {
    method: "DELETE",
  });
}

/**
 * Get available models
 */
export async function getModels(): Promise<ModelsResponse> {
  return request<ModelsResponse>("/models");
}

/**
 * Health check
 */
export async function healthCheck(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export { ApiError };
