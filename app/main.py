print("🔥 MAIN START")

from fastapi import FastAPI
from .db import engine
from .models import Base
from .routes import router

print("🔥 IMPORTS OK")

app = FastAPI()


# ✅ СОЗДАНИЕ ТАБЛИЦ (ключевой момент)
print("🔥 DB INIT")
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "alive"}


app.include_router(router)
