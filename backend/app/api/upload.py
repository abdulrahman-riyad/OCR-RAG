from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import uuid
from datetime import datetime

from app.config import settings
from app.models.document import Document, ProcessingStatus

router = APIRouter()

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.pdf'}

def validate_file(file: UploadFile) -> bool:
    """Validate file type and size"""
    if file.size > settings.MAX_UPLOAD_SIZE:
        return False
    
    ext = os.path.splitext(file.filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

@router.post("/single")
async def upload_single_file(file: UploadFile = File(...)):
    """Upload a single file"""
    if not validate_file(file):
        raise HTTPException(400, "Invalid file type or size")
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    new_filename = f"{file_id}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, new_filename)
    
    # Save file
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(500, f"Failed to save file: {str(e)}")
    
    # Create document record
    document = {
        "id": file_id,
        "title": file.filename,
        "original_file_path": file_path,
        "status": ProcessingStatus.PENDING,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    return {
        "message": "File uploaded successfully",
        "document_id": file_id,
        "filename": file.filename
    }

@router.post("/batch")
async def upload_batch_files(files: List[UploadFile] = File(...)):
    """Upload multiple files"""
    results = []
    
    for file in files:
        try:
            result = await upload_single_file(file)
            results.append(result)
        except HTTPException as e:
            results.append({
                "filename": file.filename,
                "error": e.detail
            })
    
    return {"results": results}