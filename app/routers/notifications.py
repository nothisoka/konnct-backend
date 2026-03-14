from fastapi import APIRouter, Depends
from app.dependencies import get_current_user, get_supabase

router = APIRouter()

@router.get("/")
async def get_notifications(
    user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    result = supabase.table("notifications")\
        .select("*, actor:profiles!notifications_actor_id_fkey(username, display_name, avatar_url)")\
        .eq("user_id", user["id"])\
        .order("created_at", desc=True)\
        .limit(50)\
        .execute()
    return result.data

@router.patch("/read-all")
async def mark_all_read(
    user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    supabase.table("notifications")\
        .update({"read": True})\
        .eq("user_id", user["id"])\
        .execute()
    return {"ok": True}

@router.patch("/{notification_id}/read")
async def mark_one_read(
    notification_id: str,
    user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    supabase.table("notifications")\
        .update({"read": True})\
        .eq("id", notification_id)\
        .eq("user_id", user["id"])\
        .execute()
    return {"ok": True}