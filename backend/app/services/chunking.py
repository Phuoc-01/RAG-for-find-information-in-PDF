from typing import List, Dict, Optional
import re
from app.core.config import get_settings

settings = get_settings()

class TextChunker:
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        self.separators = settings.chunk_separators
    
    def chunk_text(self, text: str) -> List[str]:
        """Chia text thành các chunks"""
        if not text or len(text) < self.chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            
            if end < text_length:
                search_start = max(start, end - self.chunk_overlap)
                best_sep = self._find_best_separator(text, search_start, end)
                
                if best_sep != -1:
                    end = best_sep + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap if end < text_length else end
        
        return chunks
    
    def _find_best_separator(self, text: str, start: int, end: int) -> int:
        """Tìm separator tốt nhất trong khoảng"""
        segment = text[start:end]
        
        for sep in self.separators:
            pos = segment.rfind(sep)
            if pos != -1:
                return start + pos
        
        return -1
    
    def chunk_document(self, text: str, metadata: Dict) -> List[Dict]:
        """Chia document và gắn metadata cho từng chunk"""
        chunks = self.chunk_text(text)
        result = []
        
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_size": len(chunk)
            })
            
            result.append({
                "text": chunk,
                "metadata": chunk_metadata,
                "id": f"{metadata.get('document_id', 'doc')}_chunk_{i}"
            })
        
        return result
    
    def chunk_with_overlap(self, text: str) -> List[str]:
        """Chia text với overlap cố định"""
        if not text:
            return []
        
        chunks = []
        step = self.chunk_size - self.chunk_overlap
        
        for i in range(0, len(text), step):
            chunk = text[i:i + self.chunk_size]
            if chunk:
                chunks.append(chunk)
        
        return chunks

# Singleton
text_chunker = TextChunker()