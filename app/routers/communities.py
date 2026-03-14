from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.dependencies import get_current_user, get_supabase

router = APIRouter()

class CommunityCreate(BaseModel):
    name: str
    description: Optional[str] = None

@router.get("/")
async def list_communities(supabase=Depends(get_supabase)):
    result = supabase.table("communities")\
        .select("*")\
        .order("created_at", desc=True)\
        .execute()
    return result.data

@router.post("/")
async def create_community(
    body: CommunityCreate,
    user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    result = supabase.table("communities").insert({
        "name": body.name,
        "description": body.description,
        "created_by": user["id"]
    }).execute()
    # Auto-join creator as admin
    supabase.table("community_members").insert({
        "community_id": result.data[0]["id"],
        "user_id": user["id"],
        "role": "admin"
    }).execute()
    return result.data[0]

@router.get("/{community_id}")
async def get_community(community_id: str, supabase=Depends(get_supabase)):
    result = supabase.table("communities")\
        .select("*")\
        .eq("id", community_id)\
        .single()\
        .execute()
    return result.data

@router.post("/{community_id}/join")
async def join_community(
    community_id: str,
    user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    supabase.table("community_members").insert({
        "community_id": community_id,
        "user_id": user["id"]
    }).execute()
    return {"joined": True}

@router.delete("/{community_id}/join")
async def leave_community(
    community_id: str,
    user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    supabase.table("community_members")\
        .delete()\
        .eq("community_id", community_id)\
        .eq("user_id", user["id"])\
        .execute()
    return {"joined": False}

@router.get("/{community_id}/posts")
async def get_community_posts(
    community_id: str,
    supabase=Depends(get_supabase)
):
    result = supabase.table("posts")\
        .select("*, profiles(username, display_name, avatar_url), likes(count)")\
        .eq("community_id", community_id)\
        .is_("parent_post_id", None)\
        .order("created_at", desc=True)\
        .execute()
    return result.data