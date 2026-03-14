from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.dependencies import get_current_user, get_supabase

router = APIRouter()

class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

@router.get("/me")
async def get_me(user=Depends(get_current_user), supabase=Depends(get_supabase)):
    result = supabase.table("profiles").select("*").eq("id", user["id"]).single().execute()
    return result.data

@router.patch("/me")
async def update_profile(
    body: UpdateProfileRequest,
    user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    updates = {k: v for k, v in body.dict().items() if v is not None}
    result = supabase.table("profiles").update(updates).eq("id", user["id"]).execute()
    return result.data[0]

@router.get("/{username}")
async def get_profile(username: str, supabase=Depends(get_supabase)):
    result = supabase.table("profiles").select("*").eq("username", username).single().execute()
    if not result.data:
        raise HTTPException(404, "User not found")
    return result.data

@router.post("/{user_id}/follow")
async def follow_user(
    user_id: str,
    user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    supabase.table("connections").insert({
        "follower_id": user["id"], "following_id": user_id
    }).execute()
    supabase.table("notifications").insert({
        "user_id": user_id, "type": "follow", "actor_id": user["id"]
    }).execute()
    supabase.table("analytics_events").insert({
        "user_id": user["id"], "event_type": "follow_user",
        "metadata": {"followed_id": user_id}
    }).execute()
    return {"following": True}

@router.delete("/{user_id}/follow")
async def unfollow_user(
    user_id: str,
    user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    supabase.table("connections")\
        .delete().eq("follower_id", user["id"]).eq("following_id", user_id).execute()
    return {"following": False}