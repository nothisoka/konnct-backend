from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()

@router.get("/me")
@Limiter(key_func=get_remote_address).limit("10/minute")  # limit to 10 requests per minute per IP
async def verify_token(user=Depends(get_current_user)):
    return {"valid": True, "user_id": user["id"], "email": user["email"]}