from fastapi import APIRouter, Depends
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/me")
async def verify_token(user=Depends(get_current_user)):
    return {"valid": True, "user_id": user["id"], "email": user["email"]}