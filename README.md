# RAG for Finding Information in PDF

Hệ thống hỏi đáp thông minh (RAG) cho phép tải lên tài liệu PDF và trò chuyện với nội dung của chúng. Câu trả lời được sinh ra dựa trên tài liệu thực tế, kèm trích dẫn nguồn cụ thể (tên file, số trang, độ tương đồng).


## 📋 Mục lục

- [Giới thiệu](#-giới-thiệu)
- [Tính năng](#-tính-năng)
- [Kiến trúc](#-kiến-trúc)
- [Cài đặt](#-cài-đặt)

---

## Giới thiệu

**RAG for Finding Information in PDF** là một hệ thống **Retrieval-Augmented Generation (RAG)** cho phép người dùng:

- **Tải lên** các tài liệu PDF, DOCX, TXT, MD, CSV
- **Đặt câu hỏi** bằng ngôn ngữ tự nhiên (tiếng Việt hoặc tiếng Anh)
- **Nhận câu trả lời** chính xác dựa trên tài liệu, có **trích dẫn nguồn** cụ thể

### Tại sao dùng RAG?

| Vấn đề | LLM thuần | **RAG System** |
|--------|-----------|----------------|
| Hallucination | ❌ Bịa thông tin | ✅ Dựa trên tài liệu |
| Kiến thức | ⚠️ Chỉ đến cutoff date | ✅ Cập nhật liên tục |
| Citation | ❌ Không có | ✅ Có (file, trang, score) |
| Tài liệu riêng | ❌ Không biết | ✅ Có thể hỏi |
| Chi phí | ❌ Fine-tune tốn kém | ✅ Không cần |

---

## Tính năng

### Quản lý tài liệu

- **Upload đa định dạng**: PDF, DOCX, TXT, MD, CSV
- **Status tracking real-time**: `pending` → `processing` → `ready`/`error`
- **Auto polling**: Tự động cập nhật khi xử lý xong
- **Xóa tài liệu**: Xóa cả file, vector, và record
- **Giới hạn 10MB/file**

### Chat với RAG

- **Hỏi đáp tự nhiên**: Tiếng Việt hoặc tiếng Anh
- **Citation đầy đủ**: Tên file, số trang, đoạn trích, score
- **Multi-turn conversation**: Lưu 5 tin nhắn gần nhất
- **Chọn tài liệu**: Filter theo document cụ thể
- **Xử lý bất đồng bộ**: Không block UI

### Giao diện

- **Design system**: Custom colors (moss, paper, ink)
- **Responsive**: Hoạt động trên desktop
- **Smooth UX**: Loading states, typing indicator
- **Error handling**: Thông báo lỗi rõ ràng

---

## Kiến trúc

### Sơ đồ tổng quan

```text
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Next.js Frontend (http://localhost:3000)             │  │
│  │  - Sidebar: Upload + Document list                    │  │
│  │  - ChatPanel: Chat UI + Sources display               │  │
│  │  - Hooks: useChat, useDocuments                       │  │
│  │  - API Client: api-client.ts                          │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST (JSON)
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      API LAYER (FastAPI)                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Routes:                                              │  │
│  │  - POST /api/v1/files/upload                          │  │
│  │  - POST /api/v1/chat                                  │  │
│  │  - GET  /api/v1/documents                             │  │
│  │  - DELETE /api/v1/documents/{id}                      │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    SERVICE LAYER                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  - file_processor: Extract text từ PDF/DOCX/TXT       │  │
│  │  - text_chunker: Chunking với overlap                 │  │
│  │  - process_document_background: Background task       │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      CORE LAYER                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  - rag_chain: RAG orchestration                       │  │
│  │  - vector_store: PGVector wrapper                     │  │
│  │  - embedding_service: Gemini embedding                │  │
│  │  - config: Settings                                   │  │
│  │  - database: SQLAlchemy session                       │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      DATA LAYER                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  PostgreSQL 16 + pgvector                             │  │
│  │  - documents                                          │  │
│  │  - langchain_pg_collection                            │  │
│  │  - langchain_pg_embedding                             │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  File System (data/uploads/)                          │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Google Gemini API    │
              │  - gemini-3.6-flash    │
              │  - gemini-embedding-001│
              └────────────────────────┘
```

---

### Data flow

#### Luồng Upload tài liệu
```text
[User] Chọn file PDF
   │
   ▼
[Frontend] POST /api/v1/files/upload
   │
   ▼
[API] files.py: upload_file()
   ├─ Validate file (size, extension)
   ├─ Lưu file vào data/uploads/
   ├─ Tạo record documents (status=PENDING)
   ├─ Trigger background task
   └─ Trả response ngay (202 Accepted)
   │
   ▼ (background, async)
[Service] process_document_background()
   ├─ Update status=PROCESSING
   │
   ├─ [1] Extract text
   │   └─ file_processor.extract_text()
   │       ├─ PDF: pypdf
   │       ├─ DOCX: python-docx
   │       ├─ TXT/MD: đọc raw
   │       └─ CSV: parse
   │
   ├─ [2] Chunking
   │   └─ text_chunker.chunk_document()
   │       ├─ chunk_size=1000, overlap=200
   │       └─ Mỗi chunk có metadata (document_id, source, chunk_index)
   │
   ├─ [3] Embedding
   │   └─ embedding_service.embed_documents()
   │       └─ Gọi Gemini API (gemini-embedding-001)
   │       └─ Nhận vector 3072 dims
   │
   ├─ [4] Store vector
   │   └─ vector_store.add_documents()
   │       └─ INSERT INTO langchain_pg_embedding
   │
   └─ Update status=READY, chunks_count, processing_time
```


#### Luồng Chat
```text
[User] Gõ câu hỏi: "RAG là gì?"
   │
   ▼
[Frontend] useChat.sendMessage()
   ├─ Thêm user message vào UI
   ├─ Chuẩn bị history
   └─ POST /api/v1/chat
   │
   ▼
[API] chat.py: chat()
   ├─ Validate message
   └─ rag_chain.ask()
   │
   ▼
[Core] RAGChain.ask()
   │
   ├─ [1] Retrieve
   │   └─ _retrieve_documents(question, document_ids)
   │       ├─ Nếu có document_ids: filter theo từng doc
   │       ├─ Ngược lại: search toàn bộ collection
   │       └─ vector_store.similarity_search(query, k=5)
   │           └─ SELECT ... ORDER BY embedding <=> query_embedding
   │           └─ Trả về top-5 chunks + distance
   │
   ├─ [2] Format context
   │   └─ _format_context(docs)
   │       └─ "[Tài liệu 1: file.pdf, trang 5 (85%)]\n{content}..."
   │
   ├─ [3] Build prompt
   │   └─ System prompt + context + chat_history + question
   │
   ├─ [4] Call LLM
   │   └─ Gemini API (gemini-3.6-flash)
   │       └─ Nhận câu trả lời
   │
   ├─ [5] Format sources
   │   └─ Convert distance → similarity
   │       └─ similarity = 1 - distance/2
   │
   └─ Return {answer, sources, has_context}
   │
   ▼
[Frontend] Hiển thị answer + sources
```

#### Luồng xóa tài liệu
```text
[User] Click X trên document
   │
   ▼
[Frontend] DELETE /api/v1/documents/{id}
   │
   ▼
[API] documents.py: delete_document()
   ├─ [1] Xóa vector embeddings
   │   └─ vector_store.delete_by_document_id()
   │       └─ DELETE FROM langchain_pg_embedding WHERE cmetadata->>'document_id' = ?
   │
   ├─ [2] Xóa file trên disk
   │   └─ file_processor.delete_file()
   │
   ├─ [3] Xóa record
   │   └─ DELETE FROM documents WHERE id = ?
   │
   └─ Return success
   │
   ▼
[Frontend] Optimistic update — xóa doc khỏi UI ngay
```

---

# Set Up (With Linux - Ubuntu)


## 📋 Yêu cầu hệ thống

Trước khi bắt đầu, đảm bảo máy bạn đã cài:

| Phần mềm | Version tối thiểu | Kiểm tra |
|----------|-------------------|----------|
| **Git** | 2.30+ | `git --version` |
| **Docker** | 20.10+ | `docker --version` |
| **Docker Compose** | 2.0+ | `docker compose version` |
| **Node.js** (nếu dev FE local) | 18.17+ | `node --version` |
| **Python** (nếu dev BE local) | 3.12+ | `python --version` |

### Cài đặt Docker (nếu chưa có)

**Ubuntu/Debian**:
```bash
# Update
sudo apt update

# Cài Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Cài Docker Compose plugin
sudo apt install docker-compose-plugin

# Thêm user vào group docker (không cần sudo mỗi lần)
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker compose version

# Build frontend
cd frontend
npm install
npm run dev (run frontend)

# Build backend - Have .venv (virtual environment)
cd backend
install -r requirments

# Run All - have to set .env based on .env.example and change API_KEY
docker compose up --build

