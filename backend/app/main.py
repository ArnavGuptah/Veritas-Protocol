from fastapi import FastAPI

app = FastAPI(
    title="Veritas Protocol",
    version="0.1.0",
    description="Trust Layer for AI"
)

@app.get("/")
def root():
    return {
        "project": "Veritas Protocol",
        "status": "Running"
    }