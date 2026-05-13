from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# =====================================================
# AUTH
# =====================================================

class PsychologistCreate(BaseModel):
    email: str
    password: str


class PsychologistOut(BaseModel):
    id: str
    email: str
    created_at: datetime
    role: str

    class Config:
        from_attributes = True


# =====================================================
# CLIENTS
# =====================================================

class ClientCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class ClientOut(BaseModel):
    id: str
    psychologist_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# =====================================================
# SESSIONS
# =====================================================

class SessionCreate(BaseModel):
    client_id: str
    session_date: Optional[datetime] = None
    title: Optional[str] = None
    duration_minutes: Optional[int] = None
    status: Optional[str] = "planned"


class SessionOut(BaseModel):
    id: str
    psychologist_id: str
    client_id: str

    session_date: Optional[datetime] = None
    title: Optional[str] = None
    duration_minutes: Optional[int] = None

    audio_url: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None

    status: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# =====================================================
# AUDIO
# =====================================================

class AudioUpdate(BaseModel):
    audio_url: str


# =====================================================
# TRANSCRIPT
# =====================================================

class TranscriptUpdate(BaseModel):
    transcript: str
