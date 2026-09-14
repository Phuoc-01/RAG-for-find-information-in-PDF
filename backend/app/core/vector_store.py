from typing import List, Dict, Optional, Tuple
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import DistanceStrategy
from langchain_core.documents import Document as LangchainDocument
from sqlalchemy import text

from app.core.database import engine
from app.core.config import get_settings
from app.core.embeddings import embedding_service

settings = get_settings()

def _resolve_distance_strategy(name: str) -> DistanceStrategy:
    """Map string từ config sang DistanceStrategy enum."""
    mapping = {
        "cosine": DistanceStrategy.COSINE,
        "l2": DistanceStrategy.EUCLIDEAN,
        "euclidean": DistanceStrategy.EUCLIDEAN,
        "ip": DistanceStrategy.MAX_INNER_PRODUCT,
        "inner_product": DistanceStrategy.MAX_INNER_PRODUCT,
    }
    return mapping.get(name.lower(), DistanceStrategy.COSINE)

class VectorStore:
    def __init__(self):
        self.connection_string = settings.database_url
        self.collection_name = settings.vector_collection
        self.embedding_function = embedding_service.embeddings

        self.vector_store = PGVector(
            embeddings=self.embedding_function,
            collection_name=self.collection_name,
            connection=self.connection_string,
            distance_strategy=_resolve_distance_strategy(settings.vector_distance),
            use_jsonb=True,
        )
        
    # ADD

    def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict],
        ids: List[str]
    ) -> List[str]:
        """Thêm documents vào vector store"""
        try:
            documents = [
                LangchainDocument(page_content=text, metadata=metadata)
                for text, metadata in zip(texts, metadatas)
            ]

            return self.vector_store.add_documents(documents=documents, ids=ids)
        except Exception as e:
            raise RuntimeError(f"Failed to add documents to vector store: {str(e)}")

    # SEARCH

    def similarity_search(
        self, 
        query: str,
        k: Optional[int] = None
    ) -> List[Tuple[LangchainDocument, float]]:
        """Tìm kiếm similar documents"""
        if k is None:
            k = settings.vector_top_k

        try:
            return self.vector_store.similarity_search_with_score(
                query=query,
                k=k
            )
        except Exception as e:
            raise RuntimeError(f"Failed to search vector store: {str(e)}")

    def similarity_search_by_document(
        self, 
        query: str, 
        document_id: str, 
        k: Optional[int] = None
    ) -> List[Tuple[LangchainDocument, float]]:
        """Tìm kiếm trong phạm vi một document"""
        if k is None:
            k = settings.vector_top_k

        try:
            filter_dict = {"document_id": document_id}
            return self.vector_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter_dict
            )
        except Exception as e:
            raise RuntimeError(f"Failed to search by document: {str(e)}")

    # DELETE

    def delete_documents(self, ids: List[str]) -> bool:
        """Xóa documents khỏi vector store"""
        try:
            self.vector_store.delete(ids=ids)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete documents: {str(e)}")

    def delete_by_document_id(self, document_id: str) -> bool:
        """Xóa tất cả chunks của một document"""
        try:
            with engine.connect() as conn:
                query = text("""
                    DELETE FROM langchain_pg_embedding 
                    WHERE cmetadata->>'document_id' = :doc_id
                """)
                conn.execute(query, {"doc_id": document_id})
                conn.commit()
                print(f"🗑️ Deleted {result.rowcount} chunks for document {document_id}")
            return True
        except Exception as e:
            print(f"❌ Error deleting: {str(e)}")
            return False

    # STATS

    def get_collection_stats(self) -> Dict:
        """Lấy thống kê collection."""
        try:
            with engine.connect() as conn:
                query = text("""
                    SELECT COUNT(*) FROM langchain_pg_embedding
                    WHERE collection_id = (
                        SELECT uuid FROM langchain_pg_collection
                        WHERE name = :collection_name
                    )
                """)
                result = conn.execute(query, {"collection_name": self.collection_name})
                count = result.scalar() or 0
            return {
                "collection_name": self.collection_name,
                "total_documents": count,
                "embedding_model": settings.gemini_embedding_model,
            }
        except Exception as e:
            return {"error": str(e)}

# Singleton
vector_store = VectorStore()