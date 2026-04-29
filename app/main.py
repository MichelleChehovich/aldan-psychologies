from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client

SUPABASE_URL = "https://zxkbsnmeoyofihwkohnr.supabase.co"
SUPABASE_KEY = "твой_anon_key"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()


class AuthData(BaseModel):
    email: str
    password: str


@app.post("/register")
def register(data: AuthData):
    res = supabase.auth.sign_up({
        "email": data.email,
        "password": data.password
    })

    if res.user is None:
        raise HTTPException(status_code=400, detail=str(res))

    return {"user_id": res.user.id}


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
