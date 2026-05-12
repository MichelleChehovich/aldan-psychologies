from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from supabase import create_client
from .deps import get_current_user
from fastapi.responses import JSONResponse
from .config import SUPABASE_URL, SUPABASE_KEY
from app.api.routes_sessions import router as sessions_router

print("🔥 APP STARTED")

#print("SUPABASE_URL =", SUPABASE_URL)
#print("SUPABASE_KEY =", SUPABASE_KEY)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

app.include_router(sessions_router)

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
    try:
        # 🔹 берём профиль из таблицы profiles
        profile_res = supabase.table("profiles") \
            .select("*") \
            .eq("id", user.id) \
            .single() \
            .execute()

        profile = profile_res.data if profile_res.data else None

        return {
            "auth": {
                "user_id": user.id,
                "email": user.email
            },
            "profile": profile
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"status": "alive"}

class ClientCreate(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    notes: str | None = None


@app.post("/clients")
def create_client(data: ClientCreate, user=Depends(get_current_user)):
    try:
        res = supabase.table("clients").insert({
            "psychologist_id": user.id,  # 🔥 связь с текущим пользователем
            "name": data.name,
            "email": data.email,
            "phone": data.phone,
            "notes": data.notes
        }).execute()

        return res.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/clients")
def get_clients(user=Depends(get_current_user)):
    res = supabase.table("clients") \
        .select("*") \
        .eq("psychologist_id", user.id) \
        .execute()

    return res.data
