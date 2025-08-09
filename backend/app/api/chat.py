from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
from pydantic import BaseModel

from app.config import settings
from app.services.rag import rag_service
from openai import OpenAI

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    document_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    sources: Optional[list] = None

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with documents using RAG"""
    try:
        # If no OpenAI key, return a placeholder response
        if settings.OPENAI_API_KEY == "placeholder-openai-key":
            return ChatResponse(
                message="Chat functionality requires an OpenAI API key. Please configure it in your .env file.",
                sources=None
            )
        
        # Search for relevant context
        context_results = await rag_service.search(request.message, limit=5)
        
        # Build context from search results
        context = "\n\n".join([
            f"Document {r['document_id']}: {r['snippet']}"
            for r in context_results
        ])
        
        # If specific document requested, prioritize it
        if request.document_id:
            doc_results = [r for r in context_results if r['document_id'] == request.document_id]
            if doc_results:
                context = doc_results[0]['snippet'] + "\n\n" + context
        
        # Generate response using OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        system_prompt = """You are a helpful assistant that answers questions about handwritten notes and documents. 
        Use the provided context to answer questions accurately. If the context doesn't contain relevant information, 
        say so clearly."""
        
        user_prompt = f"""Context from documents:
{context}

User question: {request.message}

Please provide a helpful answer based on the context above."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return ChatResponse(
            message=response.choices[0].message.content,
            sources=[r['document_id'] for r in context_results[:3]]
        )
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        raise HTTPException(500, f"Chat error: {str(e)}")