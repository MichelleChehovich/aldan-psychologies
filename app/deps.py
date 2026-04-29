from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client

SUPABASE_URL = "https://zxkbsnmeoyofihwkohnr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4a2Jzbm1lb3lvZmlod2tvaG5yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU5ODg2MDMsImV4cCI6MjA5MTU2NDYwM30.PTBUQPOAEVk7uVmsisrU_kUmzarRm9ySOptNBe7XmZc"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    user = supabase.auth.get_user(token)

    if not user.user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user.user
