export interface ApiSource {
  content: string;
  source: string;
  page?: number | null;
  chunk_index?: number | null;
  score: number;
  document_id: string;
}

export interface ChatResponse {
  answer: string;
  sources: ApiSource[];
  session_id: string;
  timestamp: string;
  has_context: boolean;
}

export type DocumentStatus = 'pending' | 'processing' | 'ready' | 'error';

export interface DocumentRecord {
  id: string;
  name: string;
  type: string;
  size: number;
  status: DocumentStatus;
  chunks_count: number;
  created_at: string;
  updated_at?: string;
  error_message?: string;
}

export interface UploadResponse {
  id: string;
  filename: string;
  content_type: string;
  size: number;
  status: string;
  message: string;
}

// UI cho components

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: ApiSource[];
}

export interface ChatHistoryItem {
  role: 'user' | 'assistant';
  content: string;
}

// SIDEBAR

export interface SourceItem {
  id: string;
  name: string;
  type: string;
  size: string;
  status: DocumentStatus;
}