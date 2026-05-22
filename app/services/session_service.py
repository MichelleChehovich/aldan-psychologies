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

    return (
        supabase
        .table("sessions")
        .insert({
            "psychologist_id": psychologist_id,
            "client_id": client_id,
            "session_date": (
                session_date.isoformat()
                if session_date
                else None
            ),
            "title": title,
            "duration_minutes": duration_minutes,
            "status": status
        })
        .execute()
    )


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

def get_session_by_id(
    psychologist_id: str,
    session_id: str
):
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


# =====================================================
# GET ALL CLIENT SESSIONS
# =====================================================

def get_client_sessions(
    psychologist_id: str,
    client_id: str
):
    supabase = get_supabase()

    return (
        supabase
        .table("sessions")
        .select("*")
        .eq("psychologist_id", psychologist_id)
        .eq("client_id", client_id)
        .eq("is_deleted", False)
        .order("session_date", desc=True)
        .execute()
    )


# =====================================================
# UPDATE SESSION META
# =====================================================

def update_session_meta(
    psychologist_id: str,
    session_id: str,
    data: dict
):
    supabase = get_supabase()

    return (
        supabase
        .table("sessions")
        .update(data)
        .eq("id", session_id)
        .eq("psychologist_id", psychologist_id)
        .execute()
    )


# =====================================================
# UPDATE SESSION AUDIO
# =====================================================

def update_session_audio(
    psychologist_id: str,
    session_id: str,
    audio_url: str
):
    supabase = get_supabase()

    return (
        supabase
        .table("sessions")
        .update({
            "audio_url": audio_url
        })
        .eq("id", session_id)
        .eq("psychologist_id", psychologist_id)
        .execute()
    )


# =====================================================
# UPDATE SELF ANALYSIS
# =====================================================

def update_self_analysis(
    psychologist_id: str,
    session_id: str,
    analysis_self: str
):
    supabase = get_supabase()

    return (
        supabase
        .table("sessions")
        .update({
            "analysis_self": analysis_self
        })
        .eq("id", session_id)
        .eq("psychologist_id", psychologist_id)
        .execute()
    )
