from fastapi import FastAPI

from .db import engine
from .models import Base
from .routes import router

app = FastAPI()


# 🔥 создание таблиц при старте
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


# 🏠 ROOT
@app.get("/")
def root():
    return {"status": "alive"}


# 🔌 ROUTES
app.include_router(router)
