from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RequirementBase(BaseModel):
    req_id: str
    req_name: Optional[str] = None
    text: str
    section: Optional[str] = None
    source_file: Optional[str] = None
    status: str = "Pending"
    priority: str = "Medium"
    source_type: str = "Original"
    verification_method: Optional[str] = ""
    rationale: Optional[str] = ""
    generated_code: Optional[str] = ""
    verification_status: Optional[str] = ""
    execution_log: Optional[str] = ""

class RequirementCreate(RequirementBase):
    id: str

class RequirementUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    verification_method: Optional[str] = None
    rationale: Optional[str] = None
    generated_code: Optional[str] = None
    verification_status: Optional[str] = None
    execution_log: Optional[str] = None

class RequirementResponse(RequirementCreate):
    created_at: datetime
    last_run_timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    filename: str
    title: str
    req_count: int = 0

class ProjectResponse(ProjectBase):
    last_updated: datetime

    class Config:
        from_attributes = True

class SystemLogResponse(BaseModel):
    id: int
    timestamp: datetime
    level: str
    message: str

    class Config:
        from_attributes = True
        
class ExecuteRequest(BaseModel):
    code: str
    api_key: Optional[str] = None

class IngestRequest(BaseModel):
    target_section: Optional[str] = None
    api_key: Optional[str] = None
