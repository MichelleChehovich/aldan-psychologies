import os
import uuid
import aiofiles

from fastapi import UploadFile, HTTPException

from app.supabase import get_supabase

# =====================================================
# AUDIO STORAGE
# =====================================================

TEMP_AUDIO_DIR = "storage/temp_audio"

ALLOWED_AUDIO_TYPES = [
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
    "audio/webm",
    "audio/ogg",
    "audio/mp4",
    "audio/x-m4a"
]

MAX_FILE_SIZE = 200 * 1024 * 1024

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

# =====================================================
# UPLOAD AUDIO FILE
# =====================================================

async def upload_audio_file(
    psychologist_id: str,
    session_id: str,
    file: UploadFile
):

    supabase = get_supabase()

    # -------------------------------------------------
    # CHECK SESSION EXISTS
    # -------------------------------------------------

    session_res = (
        supabase
        .table("sessions")
        .select("*")
        .eq("id", session_id)
        .eq("psychologist_id", psychologist_id)
        .single()
        .execute()
    )

    if not session_res.data:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    # -------------------------------------------------
    # VALIDATE MIME TYPE
    # -------------------------------------------------

    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported audio format"
        )

    # -------------------------------------------------
    # GENERATE SECURE FILENAME
    # -------------------------------------------------

    extension = os.path.splitext(file.filename)[1]

    secure_filename = (
        f"{session_id}_{uuid.uuid4()}{extension}"
    )

    # -------------------------------------------------
    # CREATE DIRECTORY
    # -------------------------------------------------

    os.makedirs(
        TEMP_AUDIO_DIR,
        exist_ok=True
    )

    file_path = os.path.join(
        TEMP_AUDIO_DIR,
        secure_filename
    )

    # -------------------------------------------------
    # SAVE FILE
    # -------------------------------------------------

    size = 0

    async with aiofiles.open(
        file_path,
        "wb"
    ) as out_file:

        while chunk := await file.read(1024 * 1024):

            size += len(chunk)

            if size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail="File too large"
                )

            await out_file.write(chunk)

    # -------------------------------------------------
    # SAVE AUDIO URL TO DB
    # -------------------------------------------------

    (
        supabase
        .table("sessions")
        .update({
            "audio_url": file_path
        })
        .eq("id", session_id)
        .eq("psychologist_id", psychologist_id)
        .execute()
    )

    # -------------------------------------------------
    # RESPONSE
    # -------------------------------------------------

    return {
        "status": "uploaded",
        "audio_url": file_path,
        "filename": secure_filename,
        "size_bytes": size
    }

