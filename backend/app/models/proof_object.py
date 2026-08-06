from __future__ import annotations

import hashlib
import json
import time
import uuid
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


def _canonical_hash(prev_hash: str, payload: Any) -> str:
    """Deterministic hash of (previous hash + canonical JSON of payload)."""
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256((prev_hash + blob).encode("utf-8")).hexdigest()


class ConfidenceLevel(str, Enum):
    HIGH = "high"       # >= 0.75
    MEDIUM = "medium"   # 0.4 - 0.75
    LOW = "low"          # < 0.4

    @staticmethod
    def from_score(score: float) -> "ConfidenceLevel":
        if score >= 0.75:
            return ConfidenceLevel.HIGH
        if score >= 0.4:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW


class EvidenceChunk(BaseModel):
    """A single retrieved chunk with full traceability (Feature 1)."""
    chunk_id: str
    text: str
    source: str
    similarity: float
    bm25_score: float
    fused_score: float
    document_hash: str  # sha256 of the source document, proves it wasn't altered


class Challenge(BaseModel):
    """One attack the Critic raises against the Generator's claim."""
    challenge_id: str
    target_claim: str
    objection: str
    severity: float  # 0-1, how damaging this objection is
    resolved: bool
    resolution_note: Optional[str] = None


class FactCheckResult(BaseModel):
    claim: str
    supported: bool
    supporting_evidence_ids: list[str]
    contradicting_evidence_ids: list[str]
    notes: str


class StageRecord(BaseModel):
    """Generic wrapper: every pipeline stage gets hashed the same way."""
    stage: str
    started_at: float
    finished_at: float
    payload: dict[str, Any]
    input_hash: str    # hash this stage received from the previous stage
    output_hash: str   # hash after folding this stage's payload in


class Verdict(BaseModel):
    verdict: str  # "supported" | "refuted" | "uncertain" | "unverifiable"
    confidence_score: float
    confidence_level: ConfidenceLevel
    rationale: str


class VerifiableReasoningRecord(BaseModel):
    """
    The Proof Object. This is what /ask returns and what gets anchored.
    """
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    created_at: float = Field(default_factory=time.time)

    evidence: list[EvidenceChunk]
    generator_answer: str
    challenges: list[Challenge]
    fact_checks: list[FactCheckResult]
    verdict: Verdict

    stages: list[StageRecord]  # full replay trace, in order
    root_hash: str = ""
    chain_anchor: Optional[dict[str, Any]] = None  # filled in after anchoring

    def verify_chain(self) -> bool:
        """
        Independent re-verification: recompute the hash chain from the stored
        stage payloads and confirm it matches root_hash. This is the function
        a THIRD PARTY (no LLM access needed) runs to check the record wasn't
        tampered with. This is the actual product.
        """
        prev = hashlib.sha256(self.question.encode("utf-8")).hexdigest()
        for stage in self.stages:
            if stage.input_hash != prev:
                return False
            recomputed = _canonical_hash(prev, stage.payload)
            if recomputed != stage.output_hash:
                return False
            prev = stage.output_hash
        return prev == self.root_hash

    def to_certificate(self) -> dict[str, Any]:
        """Feature 4: the human-facing summary view of the VRR."""
        return {
            "record_id": self.record_id,
            "question": self.question,
            "verdict": self.verdict.verdict,
            "confidence": round(self.verdict.confidence_score, 3),
            "confidence_level": self.verdict.confidence_level.value,
            "sources": sorted({e.source for e in self.evidence}),
            "num_evidence_chunks": len(self.evidence),
            "num_challenges_raised": len(self.challenges),
            "num_challenges_unresolved": sum(1 for c in self.challenges if not c.resolved),
            "root_hash": self.root_hash,
            "chain_anchor": self.chain_anchor,
            "chain_valid": self.verify_chain(),
        }
