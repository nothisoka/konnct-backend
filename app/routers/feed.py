from fastapi import APIRouter, Depends, Query
from app.dependencies import get_current_user, get_supabase

router = APIRouter()

@router.get("/")
async def get_feed(
    user=Depends(get_current_user),
    supabase=Depends(get_supabase),
    limit: int = Query(20, le=50),
    offset: int = Query(0)
):
    # Get IDs of people this user follows
    connections = supabase.table("connections")\
        .select("following_id").eq("follower_id", user["id"]).execute()

    following_ids = [c["following_id"] for c in connections.data]
    following_ids.append(user["id"])  # include own posts

    # Fetch their posts chronologically
    result = supabase.table("posts")\
        .select("*, profiles(username, display_name, avatar_url), likes(count)")\
        .in_("user_id", following_ids)\
        .is_("parent_post_id", None)\
        .order("created_at", desc=True)\
        .range(offset, offset + limit - 1)\
        .execute()

    return {"posts": result.data, "offset": offset, "limit": limit}

@router.get("/suggestions")
async def get_suggestions(
    user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    # Users followed by people you follow (mutual connection suggestion)
    connections = supabase.table("connections")\
        .select("following_id").eq("follower_id", user["id"]).execute()

    following_ids = [c["following_id"] for c in connections.data]

    if not following_ids:
        # Fallback: return newest users
        result = supabase.table("profiles")\
            .select("*").neq("id", user["id"]).limit(5).execute()
        return result.data

    # Find who those people follow that you don't yet
    candidates = supabase.table("connections")\
        .select("following_id, profiles!connections_following_id_fkey(username, display_name, avatar_url)")\
        .in_("follower_id", following_ids)\
        .not_.in_("following_id", following_ids + [user["id"]])\
        .limit(10).execute()

    # Deduplicate and score by frequency
    seen = {}
    for c in candidates.data:
        fid = c["following_id"]
        if fid not in seen:
            seen[fid] = {"profile": c["profiles"], "mutual_count": 0}
        seen[fid]["mutual_count"] += 1

    sorted_suggestions = sorted(seen.values(), key=lambda x: -x["mutual_count"])
    return sorted_suggestions[:5]