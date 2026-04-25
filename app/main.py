print("🔥 MAIN START")

from fastapi import FastAPI
from .db import Base, engine
from .routes import router
from . import models

print("🔥 IMPORTS OK")

app = FastAPI()

@app.get("/")
def root():
    return {"status": "alive"}

app.include_router(router)

print("🔥 DB INIT")

Base.metadata.create_all(bind=engine)


#from fastapi import FastAPI
#from .db import Base, engine
#from .routes import router
#from . import models  # 🔥 обязательно!

#print("STEP 1")

#app = FastAPI()

#print("STEP 2")

#@app.get("/")
#def root():
#    return {"status": "alive"}

#print("STEP 3")

#@app.get("/health")
#def health():
#    return {"status": "ok"}

#app.include_router(router)

#Base.metadata.create_all(bind=engine)
