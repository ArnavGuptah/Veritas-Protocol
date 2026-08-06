"""In-memory store for demo purposes. Swap for SQLite/Postgres (the brief's
stated stack) by replacing this dict with a table keyed on record_id — the
VRR is already a Pydantic model, so `record.model_dump_json()` drops
straight into a JSON/JSONB column with no schema translation needed."""

from __future__ import annotations
from app.models.proof_object import VerifiableReasoningRecord


class RecordStore:
    def __init__(self):
        self._records: dict[str, VerifiableReasoningRecord] = {}

    def save(self, record: VerifiableReasoningRecord) -> None:
        print(f"SAVING: {record.record_id}")
        self._records[record.record_id] = record
        print(self._records.keys())

    def get(self, record_id: str) -> VerifiableReasoningRecord | None:
        print(f"LOOKING FOR: {record_id}")
        return self._records.get(record_id)
        return self._records.get(record_id)

    def all_ids(self) -> list[str]:
        return list(self._records.keys())

record_store = RecordStore()
