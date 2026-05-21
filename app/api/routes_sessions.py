from fastapi import APIRouter, Depends, HTTPException

from app.deps import get_current_user
from app.schemas import SessionCreate
from app.supabase import get_supabase

from app.services.session_service import (
    get_client_sessions
)

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"]
)


# =====================================================
# CREATE SESSION
# =====================================================

@router.post("/")
def create_session(
    data: SessionCreate,
    user=Depends(get_current_user)
):
    try:
        supabase = get_supabase()

        res = supabase.table("sessions").insert({
            "psychologist_id": user.id,
            "client_id": data.client_id,
            "session_date": (
                data.session_date.isoformat()
                if data.session_date
                else None
            ),
            "title": data.title,
            "duration_minutes": data.duration_minutes,
            "status": data.status
        }).execute()

        return res.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# GET ALL SESSIONS
# =====================================================

@router.get("/")
def get_sessions(user=Depends(get_current_user)):
    try:
        supabase = get_supabase()

        res = (
            supabase
            .table("sessions")
            .select("*")
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
# GET ONE SESSION
# =====================================================

@router.get("/{session_id}")
def get_session(
    session_id: str,
    user=Depends(get_current_user)
):
    try:
        supabase = get_supabase()

        res = (
            supabase
            .table("sessions")
            .select("*")
            .eq("id", session_id)
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

# =====================================================
# GET ALL SESSIONS OF CLIENT
# =====================================================

@router.get("/client/{client_id}")
def get_sessions_by_client(
    client_id: str,
    user=Depends(get_current_user)
):
    try:
        res = get_client_sessions(
            psychologist_id=user.id,
            client_id=client_id
        )

        return res.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
