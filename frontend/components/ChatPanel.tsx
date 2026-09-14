"use client";
import { useEffect, useRef, useState } from "react";
import { Send, Sparkles, RotateCcw } from "lucide-react";
import type { Message } from "@/types";

export default function ChatPanel({
  messages,
  onSend,
  onNewChat,
  hasSources,
  isThinking,
  error = null,
}: {
  messages: Message[];
  onSend: (text: string) => void;
  onNewChat: () => void;
  hasSources: boolean;
  isThinking: boolean;
  error?: string | null;
}) {
  const [value, setValue] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const text = value.trim();
    if (!text || isThinking) return;
    onSend(text);
    setValue("");
  }

  return (
    <section className="flex h-full flex-1 flex-col bg-paper">
      {/* HEADER */}
      <div className="flex items-center justify-between border-b border-line px-6 py-4">
        <div>
          <h1 className="font-serif text-xl text-ink">My Notebook</h1>
          <p className="text-xs text-ink/45">
            Hỏi bất cứ điều gì về các tài liệu đã tải lên
          </p>
        </div>

        {messages.length > 0 && (
          <button
            onClick={onNewChat}
            className="flex items-center gap-1.5 rounded-lg border border-line bg-white px-3 py-1.5 text-xs text-ink/60 transition hover:border-moss-300 hover:bg-moss-50 hover:text-moss-700"
            aria-label="Cuộc trò chuyện mới"
          >
            <RotateCcw size={12} />
            Cuộc trò chuyện mới
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-6">
        {messages.length === 0 ? (
          <div className="mx-auto mt-16 max-w-sm text-center">
            <span className="mx-auto mb-4 flex h-11 w-11 items-center justify-center rounded-full bg-moss-100 text-moss-600">
              <Sparkles size={18} />
            </span>
            <p className="text-sm text-ink/50">
              {hasSources
                ? "Đặt câu hỏi để bắt đầu trò chuyện với tài liệu của bạn."
                : "Tải tài liệu lên ở bên trái, sau đó đặt câu hỏi tại đây."}
            </p>
          </div>
        ) : (
          <div className="mx-auto max-w-2xl space-y-5">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex ${
                  m.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div className="max-w-[85%]">
                  <div
                    className={`whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-card ${
                      m.role === "user"
                        ? "rounded-br-sm bg-moss-600 text-white"
                        : "rounded-bl-sm border border-line bg-white text-ink"
                    }`}
                  >
                    {m.content}
                  </div>

                  {m.role === "assistant" &&
                    m.sources &&
                    m.sources.length > 0 && (
                      <div className="mt-2 space-y-1">
                        <p className="px-1 text-xs font-medium text-ink/40">
                          Nguồn tham khảo:
                        </p>
                        {m.sources.map((src, idx) => (
                          <div
                            key={idx}
                            className="rounded-lg border border-line bg-white/60 px-3 py-2 text-xs text-ink/60"
                          >
                            <div className="flex items-center justify-between gap-2">
                              <span className="font-medium text-ink/80">
                                📄 {src.source}
                              </span>
                              <span className="shrink-0 text-ink/40">
                                {(src.score * 100).toFixed(1)}%
                              </span>
                            </div>
                            <p className="mt-1 line-clamp-2 text-ink/50">
                              {src.content}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                </div>
              </div>
            ))}

            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                ⚠️ {error}
              </div>
            )}

            {isThinking && (
              <div className="flex justify-start">
                <div className="flex items-center gap-1.5 rounded-2xl rounded-bl-sm border border-line bg-white px-4 py-3 shadow-card">
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-moss-500 [animation-delay:-0.3s]" />
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-moss-500 [animation-delay:-0.15s]" />
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-moss-500" />
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      <form
        onSubmit={handleSubmit}
        className="border-t border-line bg-paper px-6 py-4"
      >
        <div className="mx-auto flex max-w-2xl items-end gap-2 rounded-xl border border-line bg-white p-2 shadow-card focus-within:border-moss-500">
          <textarea
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            rows={1}
            placeholder="Đặt câu hỏi về tài liệu của bạn..."
            className="max-h-32 flex-1 resize-none bg-transparent px-2 py-1.5 text-sm text-ink outline-none placeholder:text-ink/35"
          />
          <button
            type="submit"
            disabled={!value.trim() || isThinking}
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-moss-600 text-white transition hover:bg-moss-700 disabled:cursor-not-allowed disabled:opacity-30"
            aria-label="Gửi câu hỏi"
          >
            <Send size={14} />
          </button>
        </div>
      </form>
    </section>
  );
}