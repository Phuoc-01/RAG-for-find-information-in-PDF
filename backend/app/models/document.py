from sqlalchemy import Column, String, Integer, DateTime, Text, Enum, Float
from sqlalchemy.sql import func
from app.core.database import Base
import enum
from datetime import datetime

class DocumentStatus(str, enum.Enum):
    """Trạng thái của document"""
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)
    size = Column(Integer, nullable=False)
    path = Column(String(500), nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING)
    chunks_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    error_message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "size": self.size,
            "status": self.status.value if self.status else None,
            "chunks_count": self.chunks_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "error_message": self.error_message
        }