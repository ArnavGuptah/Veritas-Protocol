from pydantic import BaseModel


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
