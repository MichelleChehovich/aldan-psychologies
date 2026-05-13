from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.supabase import get_supabase

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    supabase = get_supabase()

    user = supabase.auth.get_user(token)

    if not user.user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user.user
