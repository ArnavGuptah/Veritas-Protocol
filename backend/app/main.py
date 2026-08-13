from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router


app = FastAPI(
    title="Veritas Protocol",
    version="0.1.0",
    description="Trust Layer for AI"
)

print("========== MAIN.PY LOADED ==========")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("User middleware:", app.user_middleware)

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