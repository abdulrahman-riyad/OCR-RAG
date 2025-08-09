from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None

class DocumentCreate(DocumentBase):
    file_path: str

class Document(DocumentBase):
    id: str
    user_id: Optional[str] = None
    original_file_path: str
    processed_file_path: Optional[str] = None
    pdf_path: Optional[str] = None
    ocr_text: Optional[str] = None
    latex_content: Optional[str] = None
    status: ProcessingStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OCRResult(BaseModel):
    text: str
    confidence: float
    processing_time: float
    detected_languages: List[str]
    has_math: bool
    math_expressions: Optional[List[str]] = None

class SearchQuery(BaseModel):
    query: str
    limit: int = 10
    include_content: bool = False

class SearchResult(BaseModel):
    document_id: str
    title: str
    snippet: str
    score: float
    pdf_path: Optional[str] = None