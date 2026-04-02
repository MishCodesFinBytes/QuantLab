import os
from fastapi import FastAPI

app = FastAPI(title="Dockerized API")


@app.get("/health")
def health():
    return {"status": "ok", "environment": os.getenv("APP_ENV", "development")}


@app.get("/")
def root():
    return {"message": "Hello from Docker!"}
