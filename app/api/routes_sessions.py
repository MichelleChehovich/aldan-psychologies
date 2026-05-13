from fastapi import APIRouter, Depends, HTTPException
from app.deps import get_current_user
from app.schemas import SessionCreate
from app.main import supabase   # ← ВАЖНО: используем уже работающий client

router = APIRouter(prefix="/sessions", tags=["sessions"])


# =========================
# CREATE SESSION
# =========================
@router.post("")
def create_session(data: SessionCreate, user=Depends(get_current_user)):
    try:
        res = supabase.table("sessions").insert({
            "psychologist_id": user.id,
            "client_id": data.client_id,
            "session_date": data.session_date,
            "title": data.title,
            "duration_minutes": data.duration_minutes,
            "status": data.status
        }).execute()

        return res.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# GET ALL SESSIONS
# =========================
@router.get("")
def get_sessions(user=Depends(get_current_user)):
    try:
        res = supabase.table("sessions") \
            .select("*") \
            .eq("psychologist_id", user.id) \
            .execute()

        return res.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# GET ONE SESSION
# =========================
@router.get("/{session_id}")
def get_session(session_id: str, user=Depends(get_current_user)):
    try:
        res = supabase.table("sessions") \
            .select("*") \
            .eq("id", session_id) \
            .eq("psychologist_id", user.id) \
            .single() \
            .execute()

        return res.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
