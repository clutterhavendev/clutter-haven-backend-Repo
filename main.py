from fastapi import FastAPI

app = FastAPI(
  title="Clutterhaven",
  version="1.0.0",
)

@app.get("/")
def read_root():
    return {"message": "Welcome to ClutterHaven API"}