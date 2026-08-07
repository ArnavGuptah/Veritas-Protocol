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

    anchor = ledger.get(record_id)

    if anchor is None:
        raise HTTPException(
            status_code=404,
            detail="Ledger entry not found"
        )

    chain_valid = (proof.root_hash == anchor["root_hash"].lower())

    return {
        "record_id": record_id,
        "question": proof.question,
        "root_hash": proof.root_hash,
        "ledger_root_hash": anchor["root_hash"],
        "chain_valid": chain_valid,
        "anchored": True,
        "timestamp": anchor["timestamp"],
    }