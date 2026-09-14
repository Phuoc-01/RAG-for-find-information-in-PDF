from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,
    echo=settings.debug
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Session:
    """Dependency để lấy database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Khởi tạo database (tạo bảng)"""
    from app.models.document import Document
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")

def drop_db():
    """Xóa database (chỉ dùng trong development)"""
    Base.metadata.drop_all(bind=engine)
    print("⚠️ Database dropped!")