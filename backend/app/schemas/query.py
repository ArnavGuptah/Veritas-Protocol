from pydantic import BaseModel
from typing import Optional


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    status: str
    record_id: str
    question: str
    answer: str
    confidence_score: float
    confidence_level: str
    root_hash: str
    anchored: bool
    tx_hash: Optional[str] = None
    block_number: Optional[int] = None