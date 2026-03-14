from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class PostCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)
    parent_post_id: Optional[UUID] = None
    is_anonymous: bool = False
    community_id: Optional[UUID] = None

class PostResponse(BaseModel):
    id: UUID
    user_id: UUID
    content: str
    parent_post_id: Optional[UUID] = None
    is_anonymous: bool
    community_id: Optional[UUID] = None
    created_at: datetime