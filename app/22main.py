print("STEP 1")

from fastapi import FastAPI

print("STEP 2")

app = FastAPI()

print("STEP 3")
#from fastapi import FastAPI
from .db import Base, engine
#from .routes import router

print("APP STARTED")
app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

#app.include_router(router)

Base.metadata.create_all(bind=engine)
