from fastapi import APIRouter, HTTPException
from app.storage.record_store import record_store

router = APIRouter()


@router.get("/graph/{record_id}")
def graph(record_id: str):

    record = record_store.get(record_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Record not found",
        )

    nodes = []
    edges = []

    previous = None

    for stage in record.stages:

        nodes.append(
            {
                "id": stage.stage,
                "label": stage.stage,
                "hash": stage.output_hash,
            }
        )

        if previous:
            edges.append(
                {
                    "from": previous,
                    "to": stage.stage,
                }
            )

        previous = stage.stage

    return {
        "record_id": record.record_id,
        "nodes": nodes,
        "edges": edges,
    }