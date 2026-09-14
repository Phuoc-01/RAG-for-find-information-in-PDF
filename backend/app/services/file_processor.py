import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import uuid
from datetime import datetime

from pypdf import PdfReader
from docx import Document as DocxDocument
import markdown
import csv
import io

from app.core.config import get_settings

settings = get_settings()

class FileProcessor:
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.allowed_extensions = settings.allowed_extensions
        self.max_file_size = settings.max_file_size
    
    def save_file(self, file_data: bytes, filename: str) -> Dict:
        """Lưu file vào disk và trả về thông tin"""
        # Kiểm tra kích thước
        if len(file_data) > self.max_file_size:
            raise ValueError(f"File too large. Max size: {self.max_file_size / 1024 / 1024}MB")
        
        ext = Path(filename).suffix.lower()
        if ext not in self.allowed_extensions:
            raise ValueError(f"Unsupported file type: {ext}. Allowed: {', '.join(self.allowed_extensions)}")
        
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}_{filename}"
        file_path = self.upload_dir / safe_filename
        
        with open(file_path, "wb") as f:
            f.write(file_data)
        
        return {
            "id": file_id,
            "name": filename,
            "path": str(file_path),
            "size": len(file_data),
            "extension": ext,
            "content_type": self._get_content_type(ext)
        }
    
    def extract_text(self, file_path: str) -> str:
        """Trích xuất text từ file"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext == ".pdf":
            return self._extract_pdf(file_path)
        elif ext == ".docx":
            return self._extract_docx(file_path)
        elif ext in [".txt", ".md"]:
            return self._extract_txt(file_path)
        elif ext == ".csv":
            return self._extract_csv(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def _extract_pdf(self, file_path: str) -> str:
        """Trích xuất text từ PDF"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to extract PDF: {str(e)}")
    
    def _extract_docx(self, file_path: str) -> str:
        """Trích xuất text từ DOCX"""
        try:
            doc = DocxDocument(file_path)
            text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            return text.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to extract DOCX: {str(e)}")
    
    def _extract_txt(self, file_path: str) -> str:
        """Trích xuất text từ TXT/MD"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return text.strip()
        except UnicodeDecodeError:
            # Thử với encoding khác
            with open(file_path, 'r', encoding='latin-1') as f:
                text = f.read()
            return text.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to extract text: {str(e)}")
    
    def _extract_csv(self, file_path: str) -> str:
        """Trích xuất text từ CSV"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = []
                for row in reader:
                    rows.append(", ".join(row))
                return "\n".join(rows).strip()
        except Exception as e:
            raise RuntimeError(f"Failed to extract CSV: {str(e)}")
    
    def _get_content_type(self, ext: str) -> str:
        """Lấy content type từ extension"""
        content_types = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".csv": "text/csv"
        }
        return content_types.get(ext, "application/octet-stream")
    
    def get_file_info(self, file_path: str) -> Dict:
        """Lấy thông tin file"""
        path = Path(file_path)
        return {
            "name": path.name,
            "size": path.stat().st_size,
            "extension": path.suffix.lower(),
            "created_at": datetime.fromtimestamp(path.stat().st_ctime),
            "modified_at": datetime.fromtimestamp(path.stat().st_mtime)
        }
    
    def delete_file(self, file_path: str) -> bool:
        """Xóa file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False

# Singleton
file_processor = FileProcessor()