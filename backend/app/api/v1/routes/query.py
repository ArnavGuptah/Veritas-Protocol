from fastapi import APIRouter

from app.schemas.query import QueryRequest, QueryResponse
from app.engine.reasoning_engine import ReasoningEngine


router = APIRouter()


@router.post(
    "/query",
    response_model=QueryResponse,
)
def query(request: QueryRequest):

    engine = ReasoningEngine()

    proof = engine.process(request.question)

    anchor = proof.chain_anchor or {}

    print("========== CHAIN ANCHOR ==========")
    print("CHAIN ANCHOR TYPE:", type(anchor))
    print("CHAIN ANCHOR VALUE:", anchor)
    print("VERDICT:", proof.verdict.verdict)
    print("ROOT HASH:", proof.root_hash)
    print("==================================")

    anchored = anchor.get("status") == "anchored"

    return QueryResponse(
        status="success",
        record_id=proof.record_id,
        question=proof.question,
        answer=proof.generator_answer,
        confidence_score=proof.verdict.confidence_score,
        confidence_level=proof.verdict.confidence_level.value,
        root_hash=proof.root_hash,
        anchored=anchored,
        tx_hash=anchor.get("tx_hash"),
        block_number=anchor.get("block_number"),
    )