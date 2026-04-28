from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .models import TherapySession
from .schemas import SessionCreate, SessionOut, AudioUpdate, TranscriptUpdate

from .stt import download_audio, transcribe_audio

from .db import get_db
from . import models, schemas
from .llm import test_llm
from .auth import hash_password, verify_password, create_access_token
from .deps import get_current_user

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


# 🔐 REGISTRATION
@router.post("/register")
def register(data: schemas.PsychologistCreate, db: Session = Depends(get_db)):
    try:
        user = models.Psychologist(
            email=data.email,
            #password=data.password
            password=hash_password(data.password)
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    except Exception as e:
        return {"error": str(e)}

# 🔐 LOGIN
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.Psychologist).filter(models.Psychologist.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


# 🔒 PROTECTED ROUTE
@router.get("/me")
def me(current_user: models.Psychologist = Depends(get_current_user)):
    return current_user


# 👤 CREATE CLIENT
@router.post("/clients")
def create_client(
    data: schemas.ClientCreate,
    db: Session = Depends(get_db),
    current_user: models.Psychologist = Depends(get_current_user)
):
    client = models.Client(**data.dict(), psychologist_id=current_user.id)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


# 🤖 LLM TEST
@router.get("/llm-test")
async def llm_test():
    return await test_llm()


# =========================
# 📅 SESSIONS (TherapySession)
# =========================

# CREATE SESSION
@router.post("/sessions", response_model=SessionOut)
def create_session(
    data: SessionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    session = TherapySession(
        client_id=data.client_id,
        session_date=data.session_date,
        psychologist_id=current_user.id
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


# GET ALL SESSIONS
@router.get("/sessions", response_model=list[SessionOut])
def get_sessions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(TherapySession).filter(
        TherapySession.psychologist_id == current_user.id
    ).all()


# GET ONE SESSION
@router.get("/sessions/{session_id}", response_model=SessionOut)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    session = db.query(TherapySession).filter(
        TherapySession.id == session_id,
        TherapySession.psychologist_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Not found")

    return session


# ADD AUDIO
@router.post("/sessions/{session_id}/audio")
def add_audio(
    session_id: int,
    data: AudioUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    session = db.query(TherapySession).filter(
        TherapySession.id == session_id,
        TherapySession.psychologist_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Not found")

    session.audio_url = data.audio_url
    db.commit()

    return {"status": "audio added"}


# ADD TRANSCRIPT
@router.post("/sessions/{session_id}/transcript")
def add_transcript(
    session_id: int,
    data: TranscriptUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    session = db.query(TherapySession).filter(
        TherapySession.id == session_id,
        TherapySession.psychologist_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Not found")

    session.transcript = data.transcript
    db.commit()

    return {"status": "transcript added"}

# STT Provider Layer
@router.post("/sessions/{session_id}/process-audio")
async def process_audio(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    session = db.query(TherapySession).filter(
        TherapySession.id == session_id,
        TherapySession.psychologist_id == current_user.id
    ).first()

    if not session or not session.audio_url:
        raise HTTPException(status_code=404, detail="Audio not found")

    # 1. скачать аудио
    audio_bytes = await download_audio(session.audio_url)

    # 2. транскрибировать
    transcript = await transcribe_audio(audio_bytes)

    # 3. сохранить
    session.transcript = transcript
    session.status = "processed"

    db.commit()

    return {"status": "done", "transcript": transcript}





