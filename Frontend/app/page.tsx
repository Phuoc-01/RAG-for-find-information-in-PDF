"use client";

import { useState } from "react";
import Sidebar, { Source } from "@/components/Sidebar";
import ChatPanel, { Message } from "@/components/ChatPanel";

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function Home() {
  const [sources, setSources] = useState<Source[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isThinking, setIsThinking] = useState(false);

  function handleAddFiles(files: FileList) {
    const next: Source[] = Array.from(files).map((f) => ({
      id: crypto.randomUUID(),
      name: f.name,
      type: f.type,
      size: formatSize(f.size),
    }));
    setSources((prev) => [...prev, ...next]);
  }

  function handleRemove(id: string) {
    setSources((prev) => prev.filter((s) => s.id !== id));
  }

  // Thay hàm này bằng lời gọi API thật (ví dụ /api/chat) khi tích hợp backend.
  async function handleSend(text: string) {
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsThinking(true);

    setTimeout(() => {
      const reply: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content:
          sources.length > 0
            ? `Đây là câu trả lời mẫu dựa trên ${sources.length} tài liệu bạn đã tải lên. Hãy nối hàm handleSend với API backend của bạn để lấy câu trả lời thật.`
            : "Bạn chưa tải tài liệu nào lên. Hãy tải lên ít nhất một tài liệu để tôi có thể trả lời dựa trên nội dung đó.",
      };
      setMessages((prev) => [...prev, reply]);
      setIsThinking(false);
    }, 900);
  }

  return (
    <main className="flex h-screen w-full overflow-hidden bg-paper">
      <div className="w-[300px] shrink-0 border-r border-line">
        <Sidebar sources={sources} onAdd={handleAddFiles} onRemove={handleRemove} />
      </div>
      <ChatPanel
        messages={messages}
        onSend={handleSend}
        hasSources={sources.length > 0}
        isThinking={isThinking}
      />
    </main>
  );
}
