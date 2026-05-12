from datetime import datetime
from pydantic import BaseModel
from typing import Optional


# 🔐 AUTH

class PsychologistCreate(BaseModel):
    #email: EmailStr
    email: str
    password: str


class PsychologistOut(BaseModel):
    id: str
    email: str
    created_at: datetime
    role: str

    class Config:
        from_attributes = True


# 👤 CLIENT

class ClientCreate(BaseModel):
    name: str


class ClientOut(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True


# 📅 SESSION

class SessionCreate(BaseModel):
    client_id: str
    session_date: Optional[datetime] = None
    title: Optional[str] = None
    duration_minutes: Optional[int] = None
    status: Optional[str] = "planned"

class SessionOut(BaseModel):
    id: str
    client_id: str
    session_date: Optional[datetime] = None
    title: Optional[str] = None
    duration_minutes: Optional[int] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True

# 🎧 AUDIO

class AudioUpdate(BaseModel):
    audio_url: str


# 📝 TRANSCRIPT

class TranscriptUpdate(BaseModel):
    transcript: str
