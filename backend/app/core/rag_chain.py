from typing import List, Dict, Optional, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document as LangchainDocument
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
# from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
# from langchain_core.messages import HumanMessage, AIMessage
from app.core.config import get_settings
from app.core.vector_store import vector_store

settings = get_settings()

class RAGChain:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model
        self.temperature = settings.gemini_temperature
        self.top_k = settings.vector_top_k
        
        self.llm = ChatGoogleGenerativeAI(
            model=self.model,
            temperature=self.temperature,
            google_api_key=self.api_key,
            max_output_tokens=settings.gemini_max_tokens
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Bạn là một trợ lý AI chuyên về phân tích tài liệu. 
Nhiệm vụ của bạn là trả lời câu hỏi dựa trên nội dung tài liệu được cung cấp.

HƯỚNG DẪN:
1. Chỉ sử dụng thông tin từ CONTEXT để trả lời
2. Nếu context không có thông tin, hãy nói rõ: "Không tìm thấy thông tin trong tài liệu"
3. Trích dẫn nguồn tài liệu khi có thể (tên file, trang)
4. Trả lời bằng tiếng Việt, rõ ràng, mạch lạc
5. Nếu câu hỏi không liên quan đến tài liệu, hãy từ chối lịch sự

CONTEXT:
{context}

Lịch sử trò chuyện:
{chat_history}
"""),
            ("human", "{question}")
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    
    # RETRIEVE
      
    def _retrieve_context(self, question: str, document_ids: Optional[List[str]] = None) -> List[Tuple[str, float]]:
        """
        Retrieve documents from vector store
        Return a list of tuples (document_content, score) is sorted by score descending
        """
        
        try:
            if document_ids:
                all_docs: List[Tuple[LangchainDocument, float]] = []
                for doc_id in document_ids:
                    docs = vector_store.similarity_search_by_document(
                        query=question,
                        document_id=doc_id,
                        k=self.top_k,
                    )
                    all_docs.extend(docs)
                
                all_docs.sort(key=lambda x: x[1], reverse=True)
                return all_docs[: self.top_k]
            
            return vector_store.similarity_search(query=question, k=self.top_k)
            
        except Exception as e:
            print(f"❌ Error retrieving documents: {str(e)}")
            return []
        

    # FORMATTERS
    
    def _format_context(
        self,
        docs: List[Tuple[LangchainDocument, float]],
    ) -> str:
        """Format docs thành context string cho prompt."""
        if not docs:
            return "Không có tài liệu nào liên quan."

        parts = []
        for i, (doc, distance) in enumerate(docs, 1):
            
            similarity = max(0.0, 1.0 - (distance / 2.0))
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page")
            page_str = f", trang {page}" if page else ""
            parts.append(
                f"[Tài liệu {i}: {source}{page_str} (độ tương đồng: {similarity:.2%})]\n"
                f"{doc.page_content}"
            )
        return "\n\n---\n\n".join(parts)

    def _format_sources(
        self,
        docs: List[Tuple[LangchainDocument, float]],
        max_sources: int = 3,
    ) -> List[Dict]:
        """Format docs thành sources list cho API response."""
        sources = []
        for doc, distance in docs[:max_sources]:
            similarity = max(0.0, 1.0 - (distance / 2.0))
            
            sources.append({
                "content": doc.page_content[:200] + ("..." if len(doc.page_content) > 200 else ""),
                "source": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page"),
                "chunk_index": doc.metadata.get("chunk_index"),
                "score": float(similarity),
                "document_id": doc.metadata.get("document_id", ""),
            })
        return sources

    def _format_chat_history(self, history: Optional[List[Dict]]) -> str:
        """Format lịch sử chat."""
        if not history:
            return "Chưa có lịch sử trò chuyện."

        formatted = []
        for msg in history[-5:]:
            role = "Người dùng" if msg.get("role") == "user" else "Trợ lý"
            formatted.append(f"{role}: {msg.get('content', '')}")
        return "\n".join(formatted)
    
    def _get_chat_history(self, inputs: dict) -> str:
        """Lấy lịch sử chat"""
        history = inputs.get("history", [])
        if not history:
            return "Chưa có lịch sử trò chuyện."
        
        formatted = []
        for msg in history[-5:]:
            role = "Người dùng" if msg.get("role") == "user" else "Trợ lý"
            formatted.append(f"{role}: {msg.get('content', '')}")
        
        return "\n".join(formatted)
    
    
    # PUBLIC API
    
    def ask(
        self, 
        question: str, 
        document_ids: Optional[List[str]] = None,
        history: Optional[List[Dict]] = None
    ) -> Dict:
        """Hỏi và nhận câu trả lời"""
        try:
            docs = self._retrieve_context(question, document_ids)
            
            context = self._format_context(docs)
            chat_history = self._get_chat_history({"history": history})
            
            answer = self.chain.invoke({
                "context": context,
                "chat_history": chat_history,
                "question": question,
            })
            
            sources = self._format_sources(docs)
            
            
            return {
                "answer": answer,
                "sources": sources,
                "has_context": len(docs) > 0
            }
            
        except Exception as e:
            return {
                "answer": f"Xin lỗi, đã xảy ra lỗi: {str(e)}",
                "sources": [],
                "has_context": False
            }
    
    
    async def ask_stream(
        self,
        question: str,
        document_ids: Optional[List[str]] = None,
        history: Optional[List[Dict]] = None,
    ):
        """
        Streaming version — yield từng token.
        (Sẽ wire vào /chat/stream ở Phase 2)
        """
        try:
            docs = self._retrieve_context(question, document_ids)
            context = self._format_context(docs)
            chat_history = self._format_chat_history(history)

            async for chunk in self.chain.astream({
                "context": context,
                "chat_history": chat_history,
                "question": question,
            }):
                yield chunk

        except Exception as e:
            yield f"Xin lỗi, đã xảy ra lỗi: {str(e)}"

# Singleton
rag_chain = RAGChain()