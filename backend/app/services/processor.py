import os
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import json

from app.config import settings
from app.core.ocr import ocr_engine
from app.core.vision import vision_analyzer
from app.core.latex import latex_generator
from app.core.pdf import pdf_generator
from app.services.rag import rag_service
from app.services.storage import storage_service
from app.models.document import ProcessingStatus

class DocumentProcessor:
    def __init__(self):
        self.processing_queue = asyncio.Queue()
    
    async def process_document(self, document_id: str, file_path: str) -> Dict[str, Any]:
        """Main processing pipeline with RAG indexing"""
        result = {
            "document_id": document_id,
            "status": ProcessingStatus.PROCESSING,
            "steps": {}
        }
        
        try:
            # Step 1: Upload original to storage
            print(f"Step 1: Uploading original file for {document_id}")
            upload_success, storage_url = await storage_service.upload_file(file_path)
            if upload_success:
                result["steps"]["storage"] = {
                    "status": "completed",
                    "url": storage_url
                }
            
            # Step 2: OCR Processing
            print(f"Step 2: OCR processing for {document_id}")
            ocr_result = ocr_engine.process_image(file_path)
            result["steps"]["ocr"] = {
                "status": "completed",
                "text": ocr_result.text,
                "confidence": ocr_result.confidence
            }
            
            # Save OCR text
            ocr_path = os.path.join(settings.PROCESSED_DIR, f"{document_id}_ocr.txt")
            with open(ocr_path, 'w', encoding='utf-8') as f:
                f.write(ocr_result.text)
            
            # Step 3: Vision Analysis (if API key is set)
            if settings.OPENAI_API_KEY != "placeholder-openai-key":
                print(f"Step 3: Vision analysis for {document_id}")
                vision_result = await vision_analyzer.analyze_image(file_path, ocr_result.text)
                result["steps"]["vision"] = {
                    "status": "completed",
                    "enhanced_text": vision_result.get("enhanced_text", ocr_result.text)
                }
                enhanced_text = vision_result.get("enhanced_text", ocr_result.text)
            else:
                enhanced_text = ocr_result.text
                result["steps"]["vision"] = {"status": "skipped", "reason": "No API key"}
            
            # Step 4: Generate PDF
            print(f"Step 4: PDF generation for {document_id}")
            pdf_path = os.path.join(settings.PROCESSED_DIR, f"{document_id}.pdf")
            
            # Extract title from filename or first line
            title = os.path.basename(file_path).split('.')[0]
            
            metadata = {
                "document_id": document_id,
                "processed_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "ocr_confidence": f"{ocr_result.confidence:.1%}",
                "has_math": str(ocr_result.has_math),
                "original_file": os.path.basename(file_path)
            }
            
            pdf_generator.create_pdf(
                output_path=pdf_path,
                title=title,
                content=enhanced_text,
                metadata=metadata
            )
            
            # Upload PDF to storage
            pdf_upload_success, pdf_url = await storage_service.upload_file(pdf_path)
            
            result["steps"]["pdf"] = {
                "status": "completed",
                "path": pdf_path,
                "url": pdf_url if pdf_upload_success else pdf_path
            }
            
            # Step 5: RAG Indexing
            print(f"Step 5: RAG indexing for {document_id}")
            index_metadata = {
                "title": title,
                "document_id": document_id,
                "confidence": ocr_result.confidence,
                "has_math": ocr_result.has_math,
                "processed_date": datetime.now().isoformat(),
                "original_url": storage_url if upload_success else file_path,
                "pdf_url": pdf_url if pdf_upload_success else pdf_path
            }
            
            index_success = await rag_service.index_document(
                document_id=document_id,
                content=enhanced_text,
                metadata=index_metadata
            )
            
            result["steps"]["rag_indexing"] = {
                "status": "completed" if index_success else "failed",
                "indexed": index_success
            }
            
            # Update final status
            result["status"] = ProcessingStatus.COMPLETED
            result["summary"] = {
                "text_length": len(enhanced_text),
                "confidence": ocr_result.confidence,
                "has_math": ocr_result.has_math,
                "storage_url": storage_url if upload_success else None,
                "pdf_url": pdf_url if pdf_upload_success else None
            }
            
            # Save processing result
            result_path = os.path.join(settings.PROCESSED_DIR, f"{document_id}_result.json")
            with open(result_path, 'w') as f:
                json.dump(result, f, indent=2)
            
        except Exception as e:
            print(f"Processing error for {document_id}: {str(e)}")
            result["status"] = ProcessingStatus.FAILED
            result["error"] = str(e)
        
        return result
    
    async def get_processing_result(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get processing result for a document"""
        result_path = os.path.join(settings.PROCESSED_DIR, f"{document_id}_result.json")
        
        if os.path.exists(result_path):
            with open(result_path, 'r') as f:
                return json.load(f)
        
        return None

# Global processor instance
document_processor = DocumentProcessor()