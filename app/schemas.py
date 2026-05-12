from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


# 🔐 AUTH

class PsychologistCreate(BaseModel):
    #email: EmailStr
    email: str
    password: str


class PsychologistOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    role: str

    class Config:
        from_attributes = True


# 👤 CLIENT

class ClientCreate(BaseModel):
    name: str


class ClientOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# 📅 SESSION

class SessionCreate(BaseModel):
    client_id: int
    session_date: datetime


class SessionOut(BaseModel):
    id: int
    client_id: int
    session_date: datetime
    status: str

    class Config:
        from_attributes = True


# 🎧 AUDIO

class AudioUpdate(BaseModel):
    audio_url: str


# 📝 TRANSCRIPT

class TranscriptUpdate(BaseModel):
    transcript: str


#    SESSIONS 
class SessionCreate(BaseModel):
    client_id: str
    session_date: Optional[datetime] = None
    title: Optional[str] = None
    duration_minutes: Optional[int] = None
    status: Optional[str] = "planned"
