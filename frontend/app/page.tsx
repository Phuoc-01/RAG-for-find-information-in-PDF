"use client";

import { useChat } from "@/lib/hooks/useChat";
import { useDocuments } from "@/lib/hooks/useDocuments";
import Sidebar from "@/components/Sidebar";
import ChatPanel from "@/components/ChatPanel";
import type { SourceItem } from "@/types";

// HELPERS

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// MAIN PAGE

export default function Home() {
  const {
    documents,
    isUploading,
    uploadDocument,
    deleteDocument,
    error: documentsError,
  } = useDocuments();

  const {
    messages,
    sendMessage,
    isLoading,
    error: chatError,
    clearMessages,
  } = useChat();

  const sources: SourceItem[] = documents.map((doc) => ({
    id: doc.id,
    name: doc.name,
    type: doc.type,
    size: formatSize(doc.size),
    status: doc.status,
  }));

  const handleAddFiles = async (files: FileList) => {
    for (let i = 0; i < files.length; i++) {
      try {
        await uploadDocument(files[i]);
      } catch {
        continue;
      }
    }
  };

  const handleSendMessage = (text: string) => {
    const readyDocumentIds = documents
      .filter((d) => d.status === "ready")
      .map((d) => d.id);

    sendMessage(text, readyDocumentIds);
  };

  const handleNewChat = () => {
    clearMessages();
  };

  // RENDER
  
  return (
    <main className="flex h-screen w-full overflow-hidden bg-paper">
      <div className="w-[300px] shrink-0 border-r border-line">
        <Sidebar
          sources={sources}
          onAdd={handleAddFiles}
          onRemove={deleteDocument}
          isUploading={isUploading}
          error={documentsError}
        />
      </div>

      <ChatPanel
        messages={messages}
        onSend={handleSendMessage}
        onNewChat={handleNewChat}
        hasSources={documents.some((d) => d.status === "ready")}
        isThinking={isLoading}
        error={chatError}
      />
    </main>
  );
}