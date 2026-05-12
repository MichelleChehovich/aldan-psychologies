from fastapi import APIRouter, Depends, HTTPException

from app.deps import get_current_user
from app.models.schemas import SessionCreate

from app.services.session_service import (
    create_session,
    get_sessions,
    get_session_by_id
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


# =====================================================
# CREATE SESSION
# =====================================================

@router.post("")
def create_new_session(
    data: SessionCreate,
    user = Depends(get_current_user)
):
    res = create_session(
        psychologist_id=user.id,
        client_id=data.client_id,
        session_date=data.session_date,
        title=data.title,
        duration_minutes=data.duration_minutes,
        status=data.status
    )

    return res.data


# =====================================================
# GET ALL SESSIONS
# =====================================================

@router.get("")
def list_sessions(user = Depends(get_current_user)):
    res = get_sessions(user.id)

    return res.data


# =====================================================
# GET SESSION BY ID
# =====================================================

@router.get("/{session_id}")
def get_one_session(
    session_id: str,
    user = Depends(get_current_user)
):
    res = get_session_by_id(user.id, session_id)

    return res.data
