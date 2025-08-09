import os
import json
from typing import List, Dict, Any, Optional
import httpx
from sentence_transformers import SentenceTransformer
import numpy as np

from app.config import settings

class RAGService:
    def __init__(self):
        self.r2r_base_url = os.getenv("R2R_BASE_URL", "http://localhost:8001")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents_index = {}
        
    async def initialize_r2r(self):
        """Initialize R2R connection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.r2r_base_url}/health")
                if response.status_code == 200:
                    print("R2R connection successful")
                    return True
        except Exception as e:
            print(f"R2R connection failed: {str(e)}")
            print("Falling back to local embeddings")
            return False
    
    async def index_document(self, document_id: str, content: str, metadata: Dict[str, Any] = None):
        """Index a document in R2R or local storage"""
        try:
            # Try R2R first
            if await self._index_in_r2r(document_id, content, metadata):
                return True
            
            # Fallback to local indexing
            return self._index_locally(document_id, content, metadata)
            
        except Exception as e:
            print(f"Indexing error: {str(e)}")
            return False
    
    async def _index_in_r2r(self, document_id: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Index document in R2R"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "document_id": document_id,
                    "content": content,
                    "metadata": metadata or {}
                }
                
                response = await client.post(
                    f"{self.r2r_base_url}/api/v1/documents",
                    json=payload,
                    timeout=30.0
                )
                
                return response.status_code == 200
                
        except Exception as e:
            print(f"R2R indexing failed: {str(e)}")
            return False
    
    def _index_locally(self, document_id: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Local indexing using sentence transformers"""
        try:
            # Generate embeddings
            embeddings = self.embedding_model.encode(content)
            
            # Store in local index
            self.documents_index[document_id] = {
                "content": content,
                "metadata": metadata or {},
                "embeddings": embeddings.tolist()
            }
            
            # Save to disk
            index_path = os.path.join(settings.PROCESSED_DIR, "document_index.json")
            with open(index_path, 'w') as f:
                # Convert numpy arrays to lists for JSON serialization
                serializable_index = {}
                for doc_id, doc_data in self.documents_index.items():
                    serializable_index[doc_id] = {
                        "content": doc_data["content"],
                        "metadata": doc_data["metadata"],
                        "embeddings": doc_data["embeddings"]
                    }
                json.dump(serializable_index, f)
            
            return True
            
        except Exception as e:
            print(f"Local indexing error: {str(e)}")
            return False
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents using R2R or local search"""
        try:
            # Try R2R search first
            r2r_results = await self._search_r2r(query, limit)
            if r2r_results:
                return r2r_results
            
            # Fallback to local search
            return self._search_locally(query, limit)
            
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []
    
    async def _search_r2r(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search using R2R"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.r2r_base_url}/api/v1/search",
                    json={"query": query, "limit": limit},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json().get("results", [])
                    
        except Exception as e:
            print(f"R2R search failed: {str(e)}")
        
        return []
    
    def _search_locally(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Local semantic search"""
        try:
            # Load index if not in memory
            if not self.documents_index:
                index_path = os.path.join(settings.PROCESSED_DIR, "document_index.json")
                if os.path.exists(index_path):
                    with open(index_path, 'r') as f:
                        self.documents_index = json.load(f)
            
            if not self.documents_index:
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Calculate similarities
            results = []
            for doc_id, doc_data in self.documents_index.items():
                doc_embedding = np.array(doc_data["embeddings"])
                
                # Cosine similarity
                similarity = np.dot(query_embedding, doc_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                )
                
                # Find snippet
                content = doc_data["content"]
                snippet = self._extract_snippet(content, query)
                
                results.append({
                    "document_id": doc_id,
                    "score": float(similarity),
                    "snippet": snippet,
                    "metadata": doc_data["metadata"]
                })
            
            # Sort by score and limit
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]
            
        except Exception as e:
            print(f"Local search error: {str(e)}")
            return []
    
    def _extract_snippet(self, content: str, query: str, context_length: int = 150) -> str:
        """Extract relevant snippet from content"""
        query_lower = query.lower()
        content_lower = content.lower()
        
        # Find query in content
        index = content_lower.find(query_lower)
        
        if index == -1:
            # If exact match not found, return beginning
            return content[:context_length] + "..." if len(content) > context_length else content
        
        # Extract context around match
        start = max(0, index - context_length // 2)
        end = min(len(content), index + len(query) + context_length // 2)
        
        snippet = content[start:end]
        
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        
        return snippet

# Global RAG service instance
rag_service = RAGService()