"""
Orchestrates: Retrieve -> Generate -> Critique -> Fact-check -> Consensus,
hash-chaining every stage into a VerifiableReasoningRecord.

This is hand-rolled as a simple linear pipeline rather than a full LangGraph
state machine, on purpose: the brief's flow is linear (no branching/looping
needed for the MVP), so a state graph library would add dependency weight
without adding capability. If you want the LangGraph version for the
"we used LangGraph" story, see pipeline/langgraph_variant.py — same stages,
wrapped as nodes, same hash-chain logic reused unchanged.
"""

from __future__ import annotations
import hashlib
import json
import time
from app.models.proof_object import ConfidenceLevel, StageRecord, Verdict, VerifiableReasoningRecord
from app.pipeline.agents import run_consensus, run_critic, run_fact_checker, run_generator
from app.retrieval.retrieval import Retriever
from app.nlp.query_analyzer import analyze_query


def _hash(prev: str, payload) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256((prev + blob).encode("utf-8")).hexdigest()


def run_pipeline(question: str, retriever: Retriever,) -> VerifiableReasoningRecord:

    stages: list[StageRecord] = []
    h = hashlib.sha256(question.encode("utf-8")).hexdigest()
    analysis = analyze_query(question)

    print("\n========== QUERY ANALYSIS ==========")
    print("Original:", question)
    print("Normalized:", analysis.normalized)
    print("====================================\n")

    # --- Stage 1: Retrieval ---------------------------------------------
    t0 = time.time()
    retrieved_evidence = retriever.search(analysis.normalized, top_k=5)

    relevant_evidence = [
        e 
        for e in retrieved_evidence
        if e.fused_score >= 0.25
    ]

    print("\n========== DEBUG EVIDENCE ==========")

    print("QUESTION:", question)
    print("NORMALIZED:", analysis.normalized)

    for e in relevant_evidence:
        print(
            "CHUNK:",
            e.chunk_id,
            "| SCORE:",
            round(e.fused_score, 4),
            "| SOURCE:",
            e.source
        )

    print("====================================\n")

    print("\n========== RELEVANCE FILTER ==========")
    print("Retrieved:", len(retrieved_evidence))
    print("Admitted:", len(relevant_evidence))

    for e in retrieved_evidence:
        print(
            e.chunk_id,
            "| source:", e.source,
            "| fused:", round(e.fused_score, 3),
            "| admitted:", e in relevant_evidence,
        )

    print("======================================\n")

    payload = {
        "query_analysis": {
            "normalized": analysis.normalized,
        },
        "retrieved_evidence": [
            e.model_dump()
            for e in retrieved_evidence
        ],
        "admitted_evidence": [
            e.model_dump()
            for e in relevant_evidence
        ],
    }

    new_h = _hash(h, payload)

    stages.append(
        StageRecord(
            stage="retrieval",
            started_at=t0,
            finished_at=time.time(),
            payload=payload,
            input_hash=h,
            output_hash=new_h,
        )
    )

    h = new_h

    # --- Stage 2: Generation ---------------------------------------------
    t0 = time.time()
    answer = run_generator(question, relevant_evidence)

    print("\n========== DEBUG GENERATION ==========")
    print(answer)
    print("======================================\n")

    payload = {"answer": answer}
    new_h = _hash(h, payload)
    stages.append(StageRecord(stage="generation", started_at=t0, finished_at=time.time(),
                               payload=payload, input_hash=h, output_hash=new_h))
    h = new_h

    # --- Stage 3: Critique (adversarial attack) --------------------------
    t0 = time.time()
    challenges = run_critic(question, answer, relevant_evidence)

    print("\n========== CHALLENGES ==========")

    for challenge in challenges:
        print(
            "OBJECTION:",
            challenge.objection,
            "\nSEVERITY:",
            challenge.severity,
            "\nRESOLVED:",
            challenge.resolved,
            "\n"
        )

    print("================================\n")

    payload = {"challenges": [c.model_dump() for c in challenges]}
    new_h = _hash(h, payload)
    stages.append(StageRecord(stage="critique", started_at=t0, finished_at=time.time(),
                               payload=payload, input_hash=h, output_hash=new_h))
    h = new_h

    # --- Stage 4: Fact-checking -------------------------------------------
    t0 = time.time()
    fact_checks = run_fact_checker(answer, relevant_evidence)

    print("\n========== FACT CHECK RESULTS ==========")

    for fc in fact_checks:
        print(
            "CLAIM:",
            fc.claim,
            "\nSUPPORTED:",
            fc.supported,
            "\nNOTES:",
            fc.notes,
            "\nSUPPORTING:",
            fc.supporting_evidence_ids,
            "\n"
        )

    print("========================================\n")

    payload = {"fact_checks": [f.model_dump() for f in fact_checks]}
    new_h = _hash(h, payload)
    stages.append(StageRecord(stage="fact_check", started_at=t0, finished_at=time.time(),
                               payload=payload, input_hash=h, output_hash=new_h))
    h = new_h

    # --- Stage 5: Consensus -------------------------------------------------
    t0 = time.time()
    score, verdict_str, rationale = run_consensus(challenges, fact_checks, relevant_evidence)
    verdict = Verdict(
        verdict=verdict_str,
        confidence_score=score,
        confidence_level=ConfidenceLevel.from_score(score),
        rationale=rationale,
    )
    payload = {"verdict": verdict.model_dump()}
    new_h = _hash(h, payload)
    stages.append(StageRecord(stage="consensus", started_at=t0, finished_at=time.time(),
                               payload=payload, input_hash=h, output_hash=new_h))
    h = new_h

    record = VerifiableReasoningRecord(
        question=question,
        evidence=retrieved_evidence,
        generator_answer=answer,
        challenges=challenges,
        fact_checks=fact_checks,
        verdict=verdict,
        stages=stages,
        root_hash=h,
    )
    return record
