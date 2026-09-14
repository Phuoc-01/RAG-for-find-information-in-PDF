# app/api/routes/documents.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.vector_store import vector_store
from app.models.document import Document

router = APIRouter()


@router.get("", response_model=List[dict])
async def get_documents(db: Session = Depends(get_db)):
    """Lấy danh sách documents"""
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return [doc.to_dict() for doc in docs]


@router.get("/{doc_id}")
async def get_document(doc_id: str, db: Session = Depends(get_db)):
    """Lấy chi tiết document"""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc.to_dict()


@router.delete("/{doc_id}")
async def delete_document(doc_id: str, db: Session = Depends(get_db)):
    """Xóa document"""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Xóa vector embeddings
        vector_store.delete_by_document_id(doc_id)
        
        # Xóa file
        from app.services.file_processor import file_processor
        file_processor.delete_file(doc.path)
        
        # Xóa record
        db.delete(doc)
        db.commit()
        
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")