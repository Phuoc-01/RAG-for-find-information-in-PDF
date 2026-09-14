from typing import List, Optional
import numpy as np
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import get_settings

settings = get_settings()

class EmbeddingService:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_embedding_model
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in environment variables")
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=self.model,
            google_api_key=self.api_key
        )
    
    def embed_text(self, text: str) -> List[float]:
        """Tạo embedding cho một đoạn text"""
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            raise RuntimeError(f"Failed to embed text: {str(e)}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Tạo embeddings cho nhiều đoạn text"""
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            raise RuntimeError(f"Failed to embed documents: {str(e)}")
    
    def embed_chunks(self, chunks: List[str]) -> List[List[float]]:
        """Tạo embeddings cho chunks (với batch processing)"""
        batch_size = 10
        embeddings = []
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_embeddings = self.embed_documents(batch)
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Lấy kích thước vector embedding"""
        try:
            test_embedding = self.embed_text("test")
            return len(test_embedding)
        except Exception:
            return 3072

# Singleton
embedding_service = EmbeddingService()