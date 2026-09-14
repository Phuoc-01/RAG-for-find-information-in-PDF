# Notebook App

Giao diện đơn giản kiểu NotebookLM: tải tài liệu lên hiển thị ở thanh bên trái, khung hỏi đáp ở giữa/bên phải.

## Cài đặt

```bash
npm install
npm run dev
```

Mở http://localhost:3000

## Cấu trúc

- `app/page.tsx` — trang chính, giữ state (danh sách tài liệu, tin nhắn) và nối hai phần lại
- `components/Sidebar.tsx` — khu vực tải lên + danh sách tài liệu (bên trái)
- `components/ChatPanel.tsx` — khung hội thoại hỏi/đáp (bên phải)

## Tích hợp backend thật

Hiện tại:
- Tải file chỉ lưu tên/kích thước ở state (chưa upload lên server). Muốn lưu file thật, sửa `handleAddFiles` trong `app/page.tsx` để gọi API upload (ví dụ `/api/upload`, dùng `FormData`).
- Trả lời chat đang là dữ liệu giả lập (`setTimeout`). Sửa hàm `handleSend` trong `app/page.tsx` để gọi API thật, ví dụ:

```ts
const res = await fetch("/api/chat", {
  method: "POST",
  body: JSON.stringify({ question: text, sourceIds: sources.map(s => s.id) }),
});
const data = await res.json();
```

## Tùy biến giao diện

Bảng màu và font được khai báo trong `tailwind.config.ts` (màu `moss`, `paper`, `ink`) và `app/layout.tsx` (font Inter + Source Serif 4). Đổi ở đó để đổi phong cách tổng thể.
