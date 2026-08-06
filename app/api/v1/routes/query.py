from fastapi import APIRouter
from app.schemas.query import QueryRequest, QueryResponse
from app.engine.reasoning_engine import ReasoningEngine


router = APIRouter()

@router.post(
    "/query",
    response_model=QueryResponse
)
def query(request: QueryRequest):

    engine = ReasoningEngine()
    proof = engine.process(request.question)

    return QueryResponse(
        status="success",
        record_id=proof.record_id,
        question=proof.question,
        answer=proof.generator_answer,
        confidence_score=proof.verdict.confidence_score,
        confidence_level=proof.verdict.confidence_level.value,
        root_hash=proof.root_hash,
        anchored=True,
    )