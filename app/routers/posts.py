from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.dependencies import get_current_user, get_supabase

router = APIRouter()

class CreatePostRequest(BaseModel):
    content: str
    parent_post_id: Optional[str] = None
    is_anonymous: bool = False
    community_id: Optional[str] = None

@router.post("/")
async def create_post(
    body: CreatePostRequest,
    user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    result = supabase.table("posts").insert({
        "user_id": user["id"],
        "content": body.content,
        "parent_post_id": body.parent_post_id,
        "is_anonymous": body.is_anonymous,
        "community_id": body.community_id,
    }).execute()

    # fire analytics event
    supabase.table("analytics_events").insert({
        "user_id": user["id"],
        "event_type": "post_created",
        "metadata": {"post_id": result.data[0]["id"]}
    }).execute()

    return result.data[0]

@router.get("/{post_id}")
async def get_post(post_id: str, supabase=Depends(get_supabase)):
    result = supabase.table("posts")\
        .select("*, profiles(username, display_name, avatar_url), likes(count)")\
        .eq("id", post_id).single().execute()
    if not result.data:
        raise HTTPException(404, "Post not found")
    return result.data

@router.delete("/{post_id}")
async def delete_post(
    post_id: str,
    user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    result = supabase.table("posts")\
        .delete().eq("id", post_id).eq("user_id", user["id"]).execute()
    return {"deleted": True}

@router.post("/{post_id}/like")
async def like_post(
    post_id: str,
    user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    supabase.table("likes").insert({
        "user_id": user["id"], "post_id": post_id
    }).execute()
    supabase.table("analytics_events").insert({
        "user_id": user["id"], "event_type": "like_post",
        "metadata": {"post_id": post_id}
    }).execute()
    return {"liked": True}

@router.delete("/{post_id}/like")
async def unlike_post(
    post_id: str,
    user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    supabase.table("likes")\
        .delete().eq("user_id", user["id"]).eq("post_id", post_id).execute()
    return {"liked": False}