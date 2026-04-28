from datetime import datetime
from pydantic import BaseModel


class PsychologistCreate(BaseModel):
    email: str
    password: str


class ClientCreate(BaseModel):
    name: str


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


class AudioUpdate(BaseModel):
    audio_url: str


class TranscriptUpdate(BaseModel):
    transcript: str
