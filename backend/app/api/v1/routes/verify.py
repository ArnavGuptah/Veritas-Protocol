from fastapi import APIRouter, HTTPException
from app.storage.record_store import record_store
from app.blockchain.ledger import ledger

router = APIRouter()


@router.get("/verify/{record_id}")
def verify(record_id: str):

    proof = record_store.get(record_id)

    if proof is None:
        raise HTTPException(
            status_code=404,
            detail="Record not found"
        )

    chain_valid = ledger.verify(record_id, proof.root_hash)

    anchor = ledger.get(record_id)

    return {
        "record_id": record_id,
        "question": proof.question,
        "root_hash": proof.root_hash,
        "verified_on_chain": chain_valid,
        "block_timestamp": anchor["timestamp"],
        "submitter": anchor["submitter"],
    }