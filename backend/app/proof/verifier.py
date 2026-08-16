from __future__ import annotations

import hashlib
import json

from app.models.proof_object import VerifiableReasoningRecord


def _hash(prev: str, payload) -> str:
    blob = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )

    return hashlib.sha256(
        (prev + blob).encode("utf-8")
    ).hexdigest()


def verify_proof(
    record: VerifiableReasoningRecord,
) -> dict:
    """
    Recompute the complete reasoning hash chain and compare
    it with the stored root_hash.

    Returns:
        {
            "valid": bool,
            "stored_root_hash": str,
            "computed_root_hash": str,
            "tampered_stage": str | None,
            "message": str,
        }
    """

    if not record.stages:
        return {
            "valid": False,
            "stored_root_hash": record.root_hash,
            "computed_root_hash": "",
            "tampered_stage": None,
            "message": "No proof stages are present.",
        }

    # The first hash in the original pipeline is the hash
    # of the user's question.
    h = hashlib.sha256(
        record.question.encode("utf-8")
    ).hexdigest()

    for stage in record.stages:

        computed = _hash(
            h,
            stage.payload,
        )

        if computed != stage.output_hash:
            return {
                "valid": False,
                "stored_root_hash": record.root_hash,
                "computed_root_hash": computed,
                "tampered_stage": stage.stage,
                "message": (
                    f"Hash mismatch detected at stage "
                    f"'{stage.stage}'."
                ),
            }

        # The stage's recorded input hash must also match
        # the chain we reconstructed.
        if stage.input_hash != h:
            return {
                "valid": False,
                "stored_root_hash": record.root_hash,
                "computed_root_hash": computed,
                "tampered_stage": stage.stage,
                "message": (
                    f"Input hash mismatch detected at stage "
                    f"'{stage.stage}'."
                ),
            }

        h = computed

    if h != record.root_hash:
        return {
            "valid": False,
            "stored_root_hash": record.root_hash,
            "computed_root_hash": h,
            "tampered_stage": "root_hash",
            "message": "Final root hash does not match.",
        }

    return {
        "valid": True,
        "stored_root_hash": record.root_hash,
        "computed_root_hash": h,
        "tampered_stage": None,
        "message": "Proof hash chain is valid.",
    }