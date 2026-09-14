import type {
  ChatResponse,
  DocumentRecord,
  UploadResponse,
  ChatHistoryItem,
} from '@/types';

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// HELPER

async function handleResponse<T>(
  response: Response,
  fallbackMsg: string,
): Promise<T> {
  if (!response.ok) {
    let detail = fallbackMsg;
    try {
      const error = await response.json();
      detail = error.detail || error.message || fallbackMsg;
    } catch {
      // Nếu response không phải JSON (VD: 502 HTML) → dùng fallback
      detail = `${fallbackMsg} (HTTP ${response.status})`;
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

// API CLIENT

export const apiClient = {
  sendMessage: async (
    message: string,
    documentIds?: string[],
    history?: ChatHistoryItem[],
  ): Promise<ChatResponse> => {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        document_ids: documentIds && documentIds.length > 0 ? documentIds : null,
        history: history && history.length > 0 ? history : null,
      }),
    });
    return handleResponse<ChatResponse>(response, 'Không gửi được tin nhắn');
  },

  // UPLOAD
  
  uploadFile: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/files/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<UploadResponse>(response, 'Upload thất bại');
  },

  // DOCUMENTS
  
  getDocuments: async (): Promise<DocumentRecord[]> => {
    const response = await fetch(`${API_BASE}/documents`, {
      cache: 'no-store',
    });
    return handleResponse<DocumentRecord[]>(
      response,
      'Không tải được danh sách tài liệu',
    );
  },

  deleteDocument: async (id: string): Promise<{ message: string }> => {
    const response = await fetch(`${API_BASE}/documents/${id}`, {
      method: 'DELETE',
    });
    return handleResponse<{ message: string }>(
      response,
      'Xóa tài liệu thất bại',
    );
  },
};