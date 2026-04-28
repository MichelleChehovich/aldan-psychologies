from datetime import datetime
from pydantic import BaseModel, EmailStr


# 🔐 AUTH

class PsychologistCreate(BaseModel):
    email: EmailStr
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
