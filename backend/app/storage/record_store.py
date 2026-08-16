"""In-memory store for demo purposes. Swap for SQLite/Postgres (the brief's
stated stack) by replacing this dict with a table keyed on record_id — the
VRR is already a Pydantic model, so `record.model_dump_json()` drops
straight into a JSON/JSONB column with no schema translation needed."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.models.proof_object import VerifiableReasoningRecord


DB_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "veritas.db"
)


class RecordStore:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)

        conn.row_factory = sqlite3.Row

        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS records (
                    record_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                )
                """
            )

            conn.commit()

    def save(
        self,
        record: VerifiableReasoningRecord,
    ) -> None:

        payload = json.dumps(
            record.model_dump(),
            sort_keys=True,
            default=str,
        )

        with self._connect() as conn:

            conn.execute(
                """
                INSERT INTO records (
                    record_id,
                    payload
                )
                VALUES (?, ?)
                ON CONFLICT(record_id)
                DO UPDATE SET payload = excluded.payload
                """,
                (
                    record.record_id,
                    payload,
                ),
            )

            conn.commit()

    def get(
        self,
        record_id: str,
    ) -> VerifiableReasoningRecord | None:

        with self._connect() as conn:

            row = conn.execute(
                """
                SELECT payload
                FROM records
                WHERE record_id = ?
                """,
                (record_id,),
            ).fetchone()

        if row is None:
            return None

        payload = json.loads(
            row["payload"]
        )

        return VerifiableReasoningRecord.model_validate(
            payload
        )

    def all_ids(self) -> list[str]:

        with self._connect() as conn:

            rows = conn.execute(
                """
                SELECT record_id
                FROM records
                ORDER BY rowid DESC
                """
            ).fetchall()

        return [
            row["record_id"]
            for row in rows
        ]


record_store = RecordStore()