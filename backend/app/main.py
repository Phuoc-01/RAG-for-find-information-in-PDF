from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import files, health, chat, documents

from app.core.config import get_settings
from app.core.database import init_db

from contextlib import asynccontextmanager

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup + shutdown events."""
    
    print("Starting up...")
    init_db()
    print("Startup complete")

    yield
    print("Shutting down...")


app = FastAPI(
    title=settings.project_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.project_name}",
        "docs": "/docs"
    }