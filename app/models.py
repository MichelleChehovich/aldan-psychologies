from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger, ForeignKey
from datetime import datetime
from .db import Base

class Psychologist(Base):
    __tablename__ = "psychologists"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="psychologist")


class Client(Base):
    __tablename__ = "clients"

    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    psychologist_id = Column(Integer, ForeignKey("psychologists.id"))

    name = Column(String)
    avatar = Column(Text)
    year_birth = Column(String)
    one_session = Column(String)
    sputnik = Column(Text)
    kinder = Column(Text)
    grandsons = Column(Text)
    mother = Column(Text)
    father = Column(Text)
    residence = Column(Text)
    auto = Column(Text)
    credit_ippoteka = Column(Text)
