from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt as pyjwt
from jwt.algorithms import ECAlgorithm
import json
from supabase import create_client, Client
from app.config import settings

security = HTTPBearer()

# Hardcoded public key from:
# https://kdvmgyeyijaaunjtsypt.supabase.co/auth/v1/.well-known/jwks.json
SUPABASE_PUBLIC_KEY_JSON = json.dumps({
    "alg": "ES256",
    "crv": "P-256",
    "ext": True,
    "key_ops": ["verify"],
    "kid": "d0ca04e6-a64a-4020-a3ac-8575862a80dc",
    "kty": "EC",
    "use": "sig",
    "x": "tPD5X_vWYjoPQqA-TJEjPOKtGXTJQNVbtKVdKwc0FBE",
    "y": "wKxRPVcQik2BxVK2Bj01uWIuEpiO45YPZq57OFB49bM"
})

# Load it once at startup — no network calls needed
PUBLIC_KEY = ECAlgorithm.from_jwk(SUPABASE_PUBLIC_KEY_JSON)

def get_supabase() -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_key)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
) -> dict:
    token = credentials.credentials
    try:
        payload = pyjwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=["ES256"],
            options={"verify_aud": False}
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {
            "id": user_id,
            "email": payload.get("email")
        }
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except pyjwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Token error: {str(e)}")