from fastapi import APIRouter, HTTPException
from app.blockchain.ledger import ledger
from app.proof.verifier import verify_proof
from app.storage.record_store import record_store


router = APIRouter()


@router.get("/records/{record_id}/verify")
def verify_record(record_id: str):

    # --------------------------------------------------
    # 1. Load local proof
    # --------------------------------------------------

    record = record_store.get(record_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Record not found.",
        )

    # --------------------------------------------------
    # 2. Verify local hash chain
    # --------------------------------------------------

    local_result = verify_proof(record)

    if not local_result["valid"]:
        return {
            "record_id": record_id,
            "status": "tampered",
            "local_proof": local_result,
            "blockchain": {
                "anchored": False,
                "verified": False,
                "status": "not_checked",
                "tx_hash": None,
                "record": None,
            },
        }

    # --------------------------------------------------
    # 3. Check blockchain directly
    # --------------------------------------------------

    blockchain_record = ledger.get(record_id)
    blockchain_verified = False

    anchor = record.chain_anchor or {}

    if blockchain_record is not None:

        blockchain_verified = ledger.verify(
            record_id,
            record.root_hash,
        )

        if blockchain_verified:
            overall_status = "fully_verified"
            blockchain_status = "confirmed"

        else:
            overall_status = "blockchain_mismatch"
            blockchain_status = "mismatch"

        tx_hash = anchor.get("tx_hash") or anchor.get("transaction_hash")

        blockchain_payload = {
            "anchored": True,
            "verified": blockchain_verified,
            "status": blockchain_status,
            "tx_hash": tx_hash,
            "record": blockchain_record,
        }
        

    elif anchor.get("tx_hash"):

        # The transaction was submitted but the contract does
        # not expose the proof yet. It may still be pending.
        overall_status = "anchor_pending"
        blockchain_status = "pending"

        blockchain_payload = {
            "anchored": False,
            "verified": False,
            "status": "pending",
            "tx_hash": anchor.get("tx_hash"),
            "record": None,
        }

    else:

        overall_status = "valid_local_only"
        blockchain_status = "not_anchored"

        blockchain_payload = {
            "anchored": False,
            "verified": False,
            "status": "not_anchored",
            "tx_hash": None,
            "record": None,
        }

    # --------------------------------------------------
    # 4. Unified verification response
    # --------------------------------------------------

    return {
        "record_id": record_id,
        "status": overall_status,
        "local_proof": local_result,
        "blockchain": blockchain_payload,
    }