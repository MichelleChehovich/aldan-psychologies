print("🔥 MAIN START")

from fastapi import FastAPI
from .db import engine
from .models import Base
from .routes import router

app = FastAPI()

# create tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "alive"}

app.include_router(router)

print("🔥 APP READY")
