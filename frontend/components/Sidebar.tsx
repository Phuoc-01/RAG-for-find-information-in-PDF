"use client";
import { useRef } from "react";
import {
  FileText,
  Plus,
  X,
  FileSpreadsheet,
  FileImage,
  Loader2,
  AlertCircle,
} from "lucide-react";
import type { SourceItem } from "@/types";

export default function Sidebar({
  sources,
  onAdd,
  onRemove,
  isUploading = false,
  error = null,
}: {
  sources: SourceItem[];
  onAdd: (files: FileList) => void;
  onRemove: (id: string) => void;
  isUploading?: boolean;
  error?: string | null;
}) {
  const inputRef = useRef<HTMLInputElement>(null);

  return (
    <aside className="flex h-full w-full flex-col bg-white">
      {/* HEADER */}
      <div className="flex items-center justify-between px-5 pt-6 pb-4">
        <div>
          <p className="font-serif text-lg leading-none text-ink">Nguồn</p>
          <p className="mt-1 text-xs text-ink/50">
            {sources.length} tài liệu đã tải lên
          </p>
        </div>
      </div>

      {/* UPLOAD BUTTON */}
      <div className="px-5">
        <button
          onClick={() => inputRef.current?.click()}
          disabled={isUploading}
          className="flex w-full items-center justify-center gap-2 rounded-lg border border-dashed border-moss-300 bg-moss-50 py-2.5 text-sm font-medium text-moss-700 transition hover:border-moss-500 hover:bg-moss-100 disabled:opacity-50"
        >
          {isUploading ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              Đang tải lên...
            </>
          ) : (
            <>
              <Plus size={16} />
              Tải tài liệu lên
            </>
          )}
        </button>

        <input
          ref={inputRef}
          type="file"
          multiple
          className="hidden"
          accept=".pdf,.docx,.txt,.md,.csv"
          onChange={(e) => {
            if (e.target.files) {
              onAdd(e.target.files);
              e.target.value = "";
            }
          }}
        />
      </div>

      {error && (
        <div className="mx-5 mt-3 flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-2.5 text-xs text-red-700">
          <AlertCircle size={14} className="mt-0.5 shrink-0" />
          <span className="leading-snug">{error}</span>
        </div>
      )}

      <div className="mt-4 flex-1 overflow-y-auto px-3 pb-4">
        {sources.length === 0 ? (
          <div className="mt-10 px-3 text-center">
            <p className="text-sm text-ink/40">
              Chưa có tài liệu nào. Tải lên PDF, Word hoặc văn bản để bắt đầu
              trò chuyện với nội dung của bạn.
            </p>
          </div>
        ) : (
          <ul className="space-y-1">
            {sources.map((s) => {
              const Icon = iconFor(s.type);
              const isProcessing =
                s.status === "processing" || s.status === "pending";
              const isError = s.status === "error";

              return (
                <li
                  key={s.id}
                  className="group flex items-center gap-2.5 rounded-md px-2.5 py-2 hover:bg-moss-50"
                >
                  {/* ICON */}
                  <span
                    className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-md ${
                      isError
                        ? "bg-red-50 text-red-500"
                        : "bg-moss-100 text-moss-600"
                    }`}
                  >
                    {isProcessing ? (
                      <Loader2 size={15} className="animate-spin" />
                    ) : isError ? (
                      <AlertCircle size={15} />
                    ) : (
                      <Icon size={15} />
                    )}
                  </span>

                  {/* NAME + SIZE */}
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm text-ink">
                      {s.name}
                      {isProcessing && (
                        <span className="ml-2 text-xs text-moss-500">
                          đang xử lý...
                        </span>
                      )}
                      {isError && (
                        <span className="ml-2 text-xs text-red-500">
                          lỗi
                        </span>
                      )}
                    </p>
                    <p className="text-xs text-ink/40">{s.size}</p>
                  </div>

                  {/* DELETE BUTTON */}
                  {!isProcessing && (
                    <button
                      onClick={() => onRemove(s.id)}
                      className="shrink-0 rounded p-1 text-ink/30 opacity-0 transition hover:bg-line hover:text-ink group-hover:opacity-100"
                      aria-label={`Xóa ${s.name}`}
                    >
                      <X size={14} />
                    </button>
                  )}
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </aside>
  );
}

// HELPER

function iconFor(type: string) {
  if (type.includes("sheet") || type.includes("csv")) return FileSpreadsheet;
  if (type.includes("image")) return FileImage;
  return FileText;
}