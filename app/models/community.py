from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class CommunityCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CommunityResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime