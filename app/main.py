from fastapi import FastAPI
from .db import Base, engine
from .routes import router

Base.metadata.create_all(bind=engine)

#app = FastAPI()
app = FastAPI(
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

@app.get("/")
def root():
    return {"message": "API is running"}

app.include_router(router)
