from fastapi import FastAPI

print("🔥 STEP 1")

app = FastAPI()

print("🔥 STEP 2")

@app.get("/")
def root():
    return {"status": "alive"}

print("🔥 STEP 3")
