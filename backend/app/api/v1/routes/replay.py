from fastapi import APIRouter, HTTPException
from app.storage.record_store import record_store

router = APIRouter()


@router.get("/replay/{record_id}")
def replay(record_id: str):

    record = record_store.get(record_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Record not found",
        )

    return {
        "record_id": record.record_id,
        "question": record.question,
        "stages": record.stages,
    }