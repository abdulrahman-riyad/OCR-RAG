from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import os

from app.config import settings
from app.models.document import SearchQuery, SearchResult
from app.services.rag import rag_service
from app.services.processor import document_processor

router = APIRouter()

@router.post("/", response_model=List[SearchResult])
async def search_documents(query: SearchQuery):
    """Enhanced search using RAG"""
    try:
        # Use RAG service for semantic search
        results = await rag_service.search(query.query, query.limit)
        
        # Format results
        formatted_results = []
        for result in results:
            # Get document title from metadata or processing result
            doc_result = await document_processor.get_processing_result(result["document_id"])
            
            title = result.get("metadata", {}).get("title", f"Document {result['document_id']}")
            if doc_result:
                original_file = doc_result.get("summary", {}).get("original_file", "")
                if original_file:
                    title = os.path.basename(original_file).split('.')[0]
            
            formatted_results.append(SearchResult(
                document_id=result["document_id"],
                title=title,
                snippet=result["snippet"],
                score=result["score"],
                pdf_path=result.get("metadata", {}).get("pdf_url")
            ))
        
        return formatted_results
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        # Fallback to simple text search
        return await _simple_text_search(query)

async def _simple_text_search(query: SearchQuery) -> List[SearchResult]:
    """Fallback simple text search"""
    results = []
    
    # Get all processed documents
    processed_files = os.listdir(settings.PROCESSED_DIR)
    
    for file in processed_files:
        if not file.endswith('_ocr.txt'):
            continue
            
        file_path = os.path.join(settings.PROCESSED_DIR, file)
        document_id = file.replace('_ocr.txt', '')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Simple text search
            if query.query.lower() in content.lower():
                # Find snippet
                query_lower = query.query.lower()
                content_lower = content.lower()
                index = content_lower.find(query_lower)
                
                start = max(0, index - 50)
                end = min(len(content), index + len(query.query) + 50)
                snippet = content[start:end]
                
                if start > 0:
                    snippet = "..." + snippet
                if end < len(content):
                    snippet = snippet + "..."
                
                results.append(SearchResult(
                    document_id=document_id,
                    title=f"Document {document_id}",
                    snippet=snippet,
                    score=1.0
                ))
                
        except Exception as e:
            print(f"Error searching file {file}: {str(e)}")
    
    results.sort(key=lambda x: x.score, reverse=True)
    return results[:query.limit]

@router.get("/suggestions")
async def get_search_suggestions(q: str = Query(..., min_length=2)):
    """Get search suggestions based on indexed content"""
    # This is a placeholder - implement based on your needs
    suggestions = [
        "mathematical equations",
        "circuit diagrams",
        "algorithm trees",
        "graph theory",
        "electronics notes"
    ]
    
    # Filter suggestions based on query
    filtered = [s for s in suggestions if q.lower() in s.lower()]
    
    return {"suggestions": filtered[:5]}