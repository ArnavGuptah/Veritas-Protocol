from fastapi import FastAPI
from app.api.v1.router import api_router

app = FastAPI(
    title="Veritas Protocol",
    version="0.1.0",
    description="Trust Layer for AI"
)

app.include_router(
    api_router,
    prefix="/api/v1"
)


@app.get("/")
def root():
    return {
        "project": "Veritas Protocol",
        "status": "Running"
    }