from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .db import get_db
from . import models, schemas
from .llm import test_llm

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/psychologists")
def create_psychologist(data: schemas.PsychologistCreate, db: Session = Depends(get_db)):
    user = models.Psychologist(**data.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/clients")
def create_client(data: schemas.ClientCreate, db: Session = Depends(get_db)):
    client = models.Client(**data.dict())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("/llm-test")
async def llm_test():
    return await test_llm()
