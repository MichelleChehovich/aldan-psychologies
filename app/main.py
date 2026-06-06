from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.deps import get_current_user
from app.supabase import get_supabase
from app.api.routes_sessions import router as sessions_router

#from app.schemas import ClientCreate
from app.schemas import ( ClientCreate,  ClientUpdate)
from datetime import datetime

print("🔥 APP STARTED")

app = FastAPI()

# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# ROUTERS
# =====================================================

app.include_router(sessions_router)


# =====================================================
# SCHEMAS
# =====================================================

class AuthData(BaseModel):
    email: str
    password: str


#class ClientCreate(BaseModel):
#    name: str
#    email: str | None = None
#    phone: str | None = None
#    notes: str | None = None


# =====================================================
# ROOT
# =====================================================

@app.get("/")
def root():
    return {"status": "alive"}


# =====================================================
# AUTH
# =====================================================

@app.post("/register")
def register(data: AuthData):
    try:
        supabase = get_supabase()

        res = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })

        if res.user is None:
            raise HTTPException(
                status_code=400,
                detail="Registration failed"
            )

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
            raise HTTPException(
                status_code=400,
                detail="Invalid credentials"
            )

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

        profile = (
            profile_res.data
            if profile_res.data
            else None
        )

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
# CLIENTS
# =====================================================

@app.post("/clients")
def create_client(
    data: ClientCreate,
    user=Depends(get_current_user)
):
    try:
        supabase = get_supabase()

        res = supabase.table("clients").insert({
            "psychologist_id": user.id,
            "name": data.name,
            "email": data.email,
            "phone": data.phone,
            "gender": data.gender,
            "birth_date": data.birth_date,
            "notes": data.notes
        }).execute()

        return res.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/clients")
def get_clients(user=Depends(get_current_user)):
    try:
        supabase = get_supabase()

        res = (
            supabase
            .table("clients")
            .select("*")
            .eq("psychologist_id", user.id)
            .eq("is_archived", False)
            .order("created_at", desc=True)
            .execute()
        )

        return res.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# UPDATE CLIENT
# =====================================================

@app.patch("/clients/{client_id}")
def update_client(
    client_id: str,
    data: ClientUpdate,
    user=Depends(get_current_user)
):
    try:

        supabase = get_supabase()

        update_data = data.model_dump(
            exclude_unset=True
        )

        res = (
            supabase
            .table("clients")
            .update(update_data)
            .eq("id", client_id)
            .eq("psychologist_id", user.id)
            .execute()
        )

        return res.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =====================================================
# GET ARCHIVED CLIENTS
# =====================================================

@app.get("/clients/archive")
def get_archived_clients(
    user=Depends(get_current_user)
):
    try:

        supabase = get_supabase()

        res = (
            supabase
            .table("clients")
            .select("*")
            .eq("psychologist_id", user.id)
            .eq("is_archived", True)
            .order("archived_at", desc=True)
            .execute()
        )

        return res.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =====================================================
# ARCHIVE CLIENT
# =====================================================

@app.patch("/clients/{client_id}/archive")
def archive_client(
    client_id: str,
    user=Depends(get_current_user)
):
    try:

        supabase = get_supabase()

        res = (
            supabase
            .table("clients")
            .update({
                "is_archived": True,
                "archived_at": datetime.utcnow().isoformat()
            })
            .eq("id", client_id)
            .eq("psychologist_id", user.id)
            .execute()
        )

        return {
            "status": "archived",
            "client_id": client_id
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =====================================================
# RESTORE CLIENT
# =====================================================

@app.patch("/clients/{client_id}/restore")
def restore_client(
    client_id: str,
    user=Depends(get_current_user)
):
    try:

        supabase = get_supabase()

        (
            supabase
            .table("clients")
            .update({
                "is_archived": False,
                "archived_at": None
            })
            .eq("id", client_id)
            .eq("psychologist_id", user.id)
            .execute()
        )

        return {
            "status": "restored",
            "client_id": client_id
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =====================================================
# GET CLIENT BY ID
# =====================================================

@app.get("/clients/{client_id}")
def get_client(
    client_id: str,
    user=Depends(get_current_user)
):
    try:

        supabase = get_supabase()

        res = (
            supabase
            .table("clients")
            .select("*")
            .eq("id", client_id)
            .eq("psychologist_id", user.id)
            .single()
            .execute()
        )

        return res.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )




