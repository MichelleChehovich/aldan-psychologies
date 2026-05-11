import os  # ← ВОТ ЭТО НУЖНО ДОБАВИТЬ

print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("SUPABASE_KEY:", os.getenv("SUPABASE_KEY"))

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client
from .config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user = supabase.auth.get_user(token)

    if not user.user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user.user
