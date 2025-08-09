from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings
from app.api import upload, process, documents, search, chat
from app.services.rag import rag_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up OCR-RAG API...")
    # Initialize RAG service
    await rag_service.initialize_r2r()
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix=f"{settings.API_V1_STR}/upload", tags=["upload"])
app.include_router(process.router, prefix=f"{settings.API_V1_STR}/process", tags=["process"])
app.include_router(documents.router, prefix=f"{settings.API_V1_STR}/documents", tags=["documents"])
app.include_router(search.router, prefix=f"{settings.API_V1_STR}/search", tags=["search"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])

@app.get("/")
async def root():
    return {
        "message": "OCR-RAG API is running",
        "version": "1.0.0",
        "docs": f"{settings.API_V1_STR}/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "r2r": "connected" if rag_service.r2r_base_url else "not configured"
        }
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)