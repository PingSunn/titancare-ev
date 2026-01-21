/**
 * TypeScript types for the chat application
 */

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export interface Session {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  model?: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
}

export interface SessionResponse {
  session_id: string;
}

export interface ModelsResponse {
  models: string[];
  default: string;
}

export interface HealthResponse {
  status: string;
  version: string;
}
