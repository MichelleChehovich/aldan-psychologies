from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

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
    user = models.Psychologist(
        email=data.email,
        password=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


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


@router.get("/llm-test")
async def llm_test():
    return await test_llm()
