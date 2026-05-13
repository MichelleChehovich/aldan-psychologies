#from app.core.supabase import get_supabase
from app.supabase import get_supabase

# =====================================================
# CREATE SESSION
# =====================================================

def create_session(
    psychologist_id: str,
    client_id: str,
    session_date=None,
    title=None,
    duration_minutes=None,
    status="planned"
):
    supabase = get_supabase()

    return supabase.table("sessions").insert({
        "psychologist_id": psychologist_id,
        "client_id": client_id,
        "session_date": session_date.isoformat() if session_date else None,
        "title": title,
        "duration_minutes": duration_minutes,
        "status": status
    }).execute()


# =====================================================
# GET ALL SESSIONS
# =====================================================

def get_sessions(psychologist_id: str):
    supabase = get_supabase()

    return (
        supabase
        .table("sessions")
        .select("*")
        .eq("psychologist_id", psychologist_id)
        .eq("is_deleted", False)
        .order("created_at", desc=True)
        .execute()
    )


# =====================================================
# GET SESSION BY ID
# =====================================================

def get_session_by_id(psychologist_id: str, session_id: str):
    supabase = get_supabase()

    return (
        supabase
        .table("sessions")
        .select("*")
        .eq("id", session_id)
        .eq("psychologist_id", psychologist_id)
        .single()
        .execute()
    )
