from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .deps import get_current_user
from app.supabase import get_supabase
from app.api.routes_sessions import router as sessions_router

print("🔥 APP STARTED")

app = FastAPI()

# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # позже заменим на frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# ROUTERS
# =====================================================

app.include_router(sessions_router)

# =====================================================
# AUTH
# =====================================================

class AuthData(BaseModel):
    email: str
    password: str


@app.post("/register")
def register(data: AuthData):
    try:
        supabase = get_supabase()

        res = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })

        if res.user is None:
            raise HTTPException(status_code=400, detail="Registration failed")

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
        supabase = get_supabase()

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


@app.get("/me")
def me(user=Depends(get_current_user)):
    try:
        supabase = get_supabase()

        profile_res = (
            supabase
            .table("profiles")
            .select("*")
            .eq("id", user.id)
            .single()
            .execute()
        )

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


# =====================================================
# ROOT
# =====================================================

@app.get("/")
def root():
    return {"status": "alive"}
