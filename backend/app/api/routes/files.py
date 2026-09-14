from typing import Any
# import os

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

import uuid
from datetime import datetime, timezone

from app.core.config import get_settings
from app.core.database import get_db
from app.models.document import Document, DocumentStatus
from app.services.file_processor import file_processor
from app.services.chunking import text_chunker
from app.core.vector_store import vector_store

settings = get_settings()
router = APIRouter()

async def process_document_background(doc_id: str):
    """Xử lý document trong background - Tạo session MỚI"""
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return
        
        doc.status = DocumentStatus.PROCESSING
        db.commit()
        
        text = file_processor.extract_text(doc.path)
        if not text:
            raise ValueError("No text extracted from document")
        
        metadata = {
            "document_id": doc.id,
            "source": doc.name,
            "type": doc.type
        }
        chunks = text_chunker.chunk_document(text, metadata)
        
        if not chunks:
            raise ValueError("No chunks created from document")
        
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        ids = [chunk["id"] for chunk in chunks]
        
        vector_store.add_documents(texts, metadatas, ids)
        
        doc.status = DocumentStatus.READY
        doc.chunks_count = len(chunks)
        doc.processing_time = (datetime.now(timezone.utc) - doc.created_at).total_seconds()
        db.commit()
        
        print(f"✅ Document {doc.name} processed with {len(chunks)} chunks")
        
    except Exception as e:
        db.rollback()
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.status = DocumentStatus.ERROR
            doc.error_message = str(e)
            db.commit()
        print(f"❌ Error processing document: {str(e)}")
    finally:
        db.close()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Upload và xử lý tài liệu"""
    
    try:
        content = await file.read()
        file_info = file_processor.save_file(content, file.filename)
        
        doc = Document(
            id=file_info["id"],
            name=file_info["name"],
            type=file_info["extension"][1:],
            size=file_info["size"],
            path=file_info["path"],
            status=DocumentStatus.PENDING
        )
        
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        if background_tasks:
            background_tasks.add_task(process_document_background, doc.id)
        else:
            await process_document_background(doc.id)
        
        return {
            "id": doc.id,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file_info["size"],
            "status": doc.status.value if doc.status else "pending",
            "message": "File uploaded and processing started"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")