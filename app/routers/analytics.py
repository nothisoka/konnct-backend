from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.dependencies import get_current_user, get_supabase

router = APIRouter()

class AnalyticsEvent(BaseModel):
    event_type: str
    metadata: Optional[dict] = None

@router.post("/event")
async def track_event(
    body: AnalyticsEvent,
    user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    supabase.table("analytics_events").insert({
        "user_id": user["id"],
        "event_type": body.event_type,
        "metadata": body.metadata
    }).execute()
    return {"tracked": True}