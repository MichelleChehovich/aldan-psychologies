from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client

# 🔐 Supabase config (временно захардкожено для теста)
SUPABASE_URL = "https://zxkbsnmeoyofihwkohnr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4a2Jzbm1lb3lvZmlod2tvaG5yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU5ODg2MDMsImV4cCI6MjA5MTU2NDYwM30.PTBUQPOAEVk7uVmsisrU_kUmzarRm9ySOptNBe7XmZc"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()


# 📦 Request schema
class AuthData(BaseModel):
    email: str
    password: str


# 📝 Register
@app.post("/register")
def register(data: AuthData):
    res = supabase.auth.sign_up({
        "email": data.email,
        "password": data.password
    })

    if res.user is None:
        raise HTTPException(status_code=400, detail=str(res))

    return {
        "user_id": res.user.id,
        "email": res.user.email
    }


# 🔐 Login
@app.post("/login")
def login(data: AuthData):
    res = supabase.auth.sign_in_with_password({
        "email": data.email,
        "password": data.password
    })

    if res.user is None:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {
        "access_token": res.session.access_token,
        "user_id": res.user.id
    }


# ❤️ Health check
@app.get("/")
def root():
    return {"status": "alive"}
