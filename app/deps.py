from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client

SUPABASE_URL = "https://gfqafwrjrixglddpiluc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdmcWFmd3JyaXJ4Z2xkZHBpbHVjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc4OTU0NzUsImV4cCI6MjA5MzQ3MTQ3NX0.9hQDdgqyQWVofEzTG4gIPHFELtOsDLU0rISEJVpx3ws"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        res = supabase.auth.get_user(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    # 🔥 максимально безопасная проверка
    user = getattr(res, "user", None)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user
