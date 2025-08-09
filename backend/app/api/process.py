from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict
import os

from app.config import settings
from app.services.processor import document_processor
from app.models.document import ProcessingStatus

router = APIRouter()

async def process_document_task(document_id: str, file_path: str):
    """Background task to process document"""
    try:
        result = await document_processor.process_document(document_id, file_path)
        print(f"Document {document_id} processed: {result['status']}")
    except Exception as e:
        print(f"Error processing document {document_id}: {str(e)}")

@router.post("/{document_id}")
async def process_document(
    document_id: str,
    background_tasks: BackgroundTasks
) -> Dict:
    """Start processing a document"""
    
    # Check if file exists
    upload_files = os.listdir(settings.UPLOAD_DIR)
    file_path = None
    
    for file in upload_files:
        if file.startswith(document_id):
            file_path = os.path.join(settings.UPLOAD_DIR, file)
            break
    
    if not file_path:
        raise HTTPException(404, "Document not found")
    
    # Add to background tasks
    background_tasks.add_task(process_document_task, document_id, file_path)
    
    return {
        "message": "Processing started",
        "document_id": document_id,
        "status": ProcessingStatus.PROCESSING
    }

@router.get("/{document_id}/status")
async def get_processing_status(document_id: str) -> Dict:
    """Get detailed processing status"""
    
    # Check for processing result
    result = await document_processor.get_processing_result(document_id)
    
    if result:
        return result
    
    # Check if file exists
    upload_files = os.listdir(settings.UPLOAD_DIR)
    for file in upload_files:
        if file.startswith(document_id):
            return {
                "document_id": document_id,
                "status": ProcessingStatus.PENDING
            }
    
    raise HTTPException(404, "Document not found")

@router.get("/{document_id}/download/{file_type}")
async def download_processed_file(document_id: str, file_type: str):
    """Download processed files"""
    from fastapi.responses import FileResponse
    
    file_mappings = {
        "pdf": f"{document_id}.pdf",
        "text": f"{document_id}_ocr.txt",
        "latex": f"{document_id}_latex.pdf",
        "result": f"{document_id}_result.json"
    }
    
    if file_type not in file_mappings:
        raise HTTPException(400, "Invalid file type")
    
    file_path = os.path.join(settings.PROCESSED_DIR, file_mappings[file_type])
    
    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found")
    
    return FileResponse(
        path=file_path,
        media_type='application/octet-stream',
        filename=file_mappings[file_type]
    )