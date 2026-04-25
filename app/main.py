from fastapi import FastAPI
from .db import Base, engine
from .routes import router
from . import models  # 🔥 обязательно!

#print("STEP 1")

app = FastAPI()

#print("STEP 2")

@app.get("/")
def root():
    return {"status": "alive"}

#print("STEP 3")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(router)

Base.metadata.create_all(bind=engine)
