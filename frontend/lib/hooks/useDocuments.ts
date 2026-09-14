import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient } from '../api-client';
import type { DocumentRecord } from '@/types';

const POLL_INTERVAL_MS = 2000;

export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // FETCH

  const fetchDocuments = useCallback(async (silent = false) => {
    if (!silent) setIsLoading(true);
    try {
      const data = await apiClient.getDocuments();
      setDocuments(data);
      setError(null);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Không tải được tài liệu';
      setError(msg);
      console.error('fetchDocuments error:', err);
    } finally {
      if (!silent) setIsLoading(false);
    }
  }, []);

  // UPLOAD

  const uploadDocument = useCallback(
    async (file: File) => {
      setIsUploading(true);
      setError(null);
      try {
        const result = await apiClient.uploadFile(file);
        await fetchDocuments(true);
        return result;
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Upload thất bại';
        setError(msg);
        console.error('uploadDocument error:', err);
        throw err;
      } finally {
        setIsUploading(false);
      }
    },
    [fetchDocuments],
  );

  // DELETE

  const deleteDocument = useCallback(
    async (id: string) => {
      setError(null);
      try {
        await apiClient.deleteDocument(id);
        setDocuments((prev) => prev.filter((d) => d.id !== id));
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Xóa thất bại';
        setError(msg);
        console.error('deleteDocument error:', err);
        await fetchDocuments(true);
        throw err;
      }
    },
    [fetchDocuments],
  );

  // POLLING — auto refresh
  
  useEffect(() => {
    const hasProcessing = documents.some(
      (d) => d.status === 'pending' || d.status === 'processing',
    );

    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
    }

    if (hasProcessing) {
      pollTimerRef.current = setInterval(() => {
        fetchDocuments(true);
      }, POLL_INTERVAL_MS);
    }

    return () => {
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current);
        pollTimerRef.current = null;
      }
    };
  }, [documents, fetchDocuments]);

  // INITIAL FETCH
  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  return {
    documents,
    isLoading,
    isUploading,
    error,
    uploadDocument,
    deleteDocument,
    refreshDocuments: fetchDocuments,
  };
}