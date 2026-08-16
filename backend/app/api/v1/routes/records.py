from fastapi import APIRouter, HTTPException
from app.storage.record_store import record_store

router = APIRouter()

@router.get("/records/{record_id}")
def get_record(record_id: str):

    record = record_store.get(record_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Record not found.",
        )

    return record.model_dump()