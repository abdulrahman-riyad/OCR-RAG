from fastapi import APIRouter, HTTPException
from typing import List, Dict
import os
import json
from datetime import datetime

from app.config import settings
from app.models.document import Document, ProcessingStatus

router = APIRouter()

def get_document_info(document_id: str) -> Dict:
    """Get document information"""
    # Check upload directory
    upload_files = os.listdir(settings.UPLOAD_DIR)
    original_file = None
    
    for file in upload_files:
        if file.startswith(document_id):
            original_file = file
            break
    
    if not original_file:
        return None
    
    # Check if processed
    ocr_file = os.path.join(settings.PROCESSED_DIR, f"{document_id}_ocr.txt")
    has_ocr = os.path.exists(ocr_file)
    
    ocr_text = None
    if has_ocr:
        with open(ocr_file, "r", encoding="utf-8") as f:
            ocr_text = f.read()
    
    return {
        "id": document_id,
        "title": original_file,
        "original_file_path": os.path.join(settings.UPLOAD_DIR, original_file),
        "status": ProcessingStatus.COMPLETED if has_ocr else ProcessingStatus.PENDING,
        "ocr_text": ocr_text,
        "created_at": datetime.fromtimestamp(
            os.path.getctime(os.path.join(settings.UPLOAD_DIR, original_file))
        ).isoformat()
    }

@router.get("/")
async def list_documents() -> List[Dict]:
    """List all documents"""
    documents = []
    
    # Get all files from upload directory
    upload_files = os.listdir(settings.UPLOAD_DIR)
    
    for file in upload_files:
        if file.endswith('.gitkeep'):
            continue
            
        document_id = file.split('.')[0]
        doc_info = get_document_info(document_id)
        if doc_info:
            documents.append(doc_info)
    
    return documents

@router.get("/{document_id}")
async def get_document(document_id: str) -> Dict:
    """Get a specific document"""
    doc_info = get_document_info(document_id)
    
    if not doc_info:
        raise HTTPException(404, "Document not found")
    
    return doc_info

@router.delete("/{document_id}")
async def delete_document(document_id: str) -> Dict:
    """Delete a document"""
    # Find and delete files
    deleted_files = []
    
    # Check upload directory
    upload_files = os.listdir(settings.UPLOAD_DIR)
    for file in upload_files:
        if file.startswith(document_id):
            os.remove(os.path.join(settings.UPLOAD_DIR, file))
            deleted_files.append(file)
    
    # Check processed directory
    processed_files = os.listdir(settings.PROCESSED_DIR)
    for file in processed_files:
        if file.startswith(document_id):
            os.remove(os.path.join(settings.PROCESSED_DIR, file))
            deleted_files.append(file)
    
    if not deleted_files:
        raise HTTPException(404, "Document not found")
    
    return {
        "message": "Document deleted successfully",
        "deleted_files": deleted_files
    }