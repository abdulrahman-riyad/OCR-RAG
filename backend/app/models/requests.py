from pydantic import BaseModel
from typing import Optional

class UploadResponse(BaseModel):
    message: str
    document_id: str
    filename: str

class ProcessResponse(BaseModel):
    message: str
    document_id: str
    status: str

class StatusResponse(BaseModel):
    document_id: str
    status: str

class DeleteResponse(BaseModel):
    message: str
    deleted_files: list[str]