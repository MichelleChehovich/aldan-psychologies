from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from supabase import create_client
from .deps import get_current_user

#SUPABASE_URL = "https://zxkbsnmeoyofihwkohnr.supabase.co"
#SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4a2Jzbm1lb3lvZmlod2tvaG5yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU5ODg2MDMsImV4cCI6MjA5MTU2NDYwM30.PTBUQPOAEVk7uVmsisrU_kUmzarRm9ySOptNBe7XmZc"
#SUPABASE_URL = "https://zxkbsnmeoyofihwkohnr.supabase.co"
SUPABASE_URL = "https://gfqafwrjrixglddpiluc.supabase.co"
#SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4a2Jzbm1lb3lvZmlod2tvaG5yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU5ODg2MDMsImV4cCI6MjA5MTU2NDYwM30.PTBUQPOAEVk7uVmsisrU_kUmzarRm9ySOptNBe7XmZc"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdmcWFmd3Jqcml4Z2xkZHBpbHVjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc4OTU0NzUsImV4cCI6MjA5MzQ3MTQ3NX0.9hQDdgqyQWVofEzTG4gIPHFELtOsDLU0rISEJVpx3ws"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()


class AuthData(BaseModel):
    email: str
    password: str


@app.post("/register")
def register(data: AuthData):
    try:
        res = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })

        if res.user is None:
            raise HTTPException(status_code=400, detail="Registration failed")

        # 👉 ВАЖНО: создаём профиль
        supabase.table("profiles").insert({
            "id": res.user.id,
            "email": res.user.email
        }).execute()

        return {
            "user_id": res.user.id,
            "email": res.user.email
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/login")
def login(data: AuthData):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })

        if res.user is None or res.session is None:
            raise HTTPException(status_code=400, detail="Invalid credentials")

        return {
            "access_token": res.session.access_token,
            "user_id": res.user.id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔥 ВОТ ЭТО ГЛАВНОЕ
@app.get("/me")
def me(user = Depends(get_current_user)):
    return {
        "user_id": user.id,
        "email": user.email
    }


@app.get("/")
def root():
    return {"status": "alive"}
