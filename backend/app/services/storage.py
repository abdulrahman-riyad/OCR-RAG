from supabase import create_client, Client
from typing import Optional, Tuple, BinaryIO
import os
from datetime import datetime
import mimetypes

from app.config import settings

class StorageService:
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.bucket_name = "documents"
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client"""
        try:
            if (settings.SUPABASE_URL != "https://placeholder.supabase.co" and 
                settings.SUPABASE_SERVICE_KEY != "placeholder-service-key"):
                
                self.supabase = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_SERVICE_KEY
                )
                
                # Ensure bucket exists
                self._ensure_bucket_exists()
                print("Supabase storage initialized")
            else:
                print("Supabase credentials not configured, using local storage")
                
        except Exception as e:
            print(f"Supabase initialization error: {str(e)}")
            self.supabase = None
    
    def _ensure_bucket_exists(self):
        """Ensure the storage bucket exists"""
        if not self.supabase:
            return
        
        try:
            # Check if bucket exists
            buckets = self.supabase.storage.list_buckets()
            bucket_names = [b['name'] for b in buckets]
            
            if self.bucket_name not in bucket_names:
                # Create bucket
                self.supabase.storage.create_bucket(
                    self.bucket_name,
                    options={"public": True}
                )
                print(f"Created bucket: {self.bucket_name}")
                
        except Exception as e:
            print(f"Bucket creation error: {str(e)}")
    
    async def upload_file(self, file_path: str, file_name: Optional[str] = None) -> Tuple[bool, str]:
        """Upload file to Supabase or local storage"""
        try:
            if not file_name:
                file_name = os.path.basename(file_path)
            
            # Add timestamp to filename to ensure uniqueness
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_name = f"{timestamp}_{file_name}"
            
            if self.supabase:
                # Upload to Supabase
                with open(file_path, 'rb') as f:
                    response = self.supabase.storage.from_(self.bucket_name).upload(
                        path=unique_name,
                        file=f,
                        file_options={"content-type": self._get_content_type(file_path)}
                    )
                
                if response.error:
                    print(f"Supabase upload error: {response.error}")
                    return False, ""
                
                # Get public URL
                url = self.supabase.storage.from_(self.bucket_name).get_public_url(unique_name)
                return True, url
            else:
                # Local storage fallback
                return True, file_path
                
        except Exception as e:
            print(f"Upload error: {str(e)}")
            return False, ""
    
    async def download_file(self, file_path: str, destination: str) -> bool:
        """Download file from Supabase"""
        try:
            if self.supabase and file_path.startswith("http"):
                # Extract path from URL
                path_parts = file_path.split(f"/{self.bucket_name}/")
                if len(path_parts) > 1:
                    file_name = path_parts[1]
                    
                    response = self.supabase.storage.from_(self.bucket_name).download(file_name)
                    
                    if response:
                        with open(destination, 'wb') as f:
                            f.write(response)
                        return True
            
            return False
            
        except Exception as e:
            print(f"Download error: {str(e)}")
            return False
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        try:
            if self.supabase and file_path.startswith("http"):
                # Extract path from URL
                path_parts = file_path.split(f"/{self.bucket_name}/")
                if len(path_parts) > 1:
                    file_name = path_parts[1]
                    
                    response = self.supabase.storage.from_(self.bucket_name).remove([file_name])
                    return not response.error
            
            # Local file deletion
            elif os.path.exists(file_path):
                os.remove(file_path)
                return True
            
            return False
            
        except Exception as e:
            print(f"Delete error: {str(e)}")
            return False
    
    def _get_content_type(self, file_path: str) -> str:
        """Get MIME type for file"""
        content_type, _ = mimetypes.guess_type(file_path)
        return content_type or 'application/octet-stream'
    
    def get_public_url(self, file_path: str) -> Optional[str]:
        """Get public URL for a file"""
        if self.supabase and not file_path.startswith("http"):
            return self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)
        return file_path

# Global storage service instance
storage_service = StorageService()