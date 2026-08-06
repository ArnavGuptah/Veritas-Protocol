"""
Feature 2: Multi-Agent Verification.

Four small, single-purpose agents instead of one LLM asked to "be careful."
Each agent's ONLY job is listed in its system prompt — this is what makes
the critic actually adversarial instead of politely agreeing with the
generator (the single biggest failure mode of naive self-critique loops).
"""

from __future__ import annotations
import uuid
from app.models.proof_object import Challenge, EvidenceChunk, FactCheckResult
from app.pipeline.llm_adapter import call_llm


GENERATOR_SYSTEM = """You are the Generator agent in a verification pipeline.
Answer the user's question using ONLY the provided evidence chunks.
Cite which chunk_id supports each claim you make. If evidence is
insufficient, say so explicitly rather than filling gaps from prior
knowledge."""

CRITIC_SYSTEM = """You are the Critic agent. Your ONLY job is to find weaknesses
in the Generator's answer: unsupported claims, single-source claims,
outdated evidence, logical gaps, or evidence that's topically related but
doesn't actually establish the claim. You are rewarded for finding real
problems and penalized for staying silent. Do not soften your objections."""

FACT_CHECKER_SYSTEM = """You are the Fact Checker agent. For each discrete
claim in the Generator's answer, decide: SUPPORTED, CONTRADICTED, or
INSUFFICIENT_EVIDENCE, based strictly on the evidence chunks provided.
You do not use outside knowledge."""

CONSENSUS_SYSTEM = """You are the Consensus agent. Given the Generator's
answer, the Critic's objections, and the Fact Checker's verdicts, produce
a final confidence score (0-1) and verdict: supported / refuted / uncertain
/ unverifiable. Unresolved high-severity challenges must pull confidence
down significantly."""


def run_generator(question: str, evidence: list[EvidenceChunk]) -> str:
    evidence_block = "\n".join(f"[{e.chunk_id}] {e.text}" for e in evidence)
    user = f"Question: {question}\n\nEvidence:\n{evidence_block}"
    return call_llm(GENERATOR_SYSTEM, user)


def run_critic(question: str, answer: str, evidence: list[EvidenceChunk]) -> list[Challenge]:
    """
    In mock mode this raises a bounded, evidence-aware set of challenges so
    the demo has something real to attack. In real mode, parse the LLM's
    structured objections (ask it for JSON) into Challenge objects the same
    way — the shape below is what your real prompt should target.
    """
    challenges: list[Challenge] = []

    # Heuristic + LLM-flavored challenge: single-source claims are always
    # worth flagging regardless of model quality — a good adversarial system
    # doesn't rely on the LLM to remember this every time.
    sources = {e.source for e in evidence}
    if len(sources) <= 1 and evidence:
        challenges.append(
            Challenge(
                challenge_id=str(uuid.uuid4())[:8],
                target_claim=answer[:80],
                objection=call_llm(CRITIC_SYSTEM, f"Q: {question}\nA: {answer}\nEvidence sources: {sources}", seed=1),
                severity=0.3,
                resolved=False,
            )
        )

    low_conf_chunks = [e for e in evidence if e.fused_score < 0.25]
    if low_conf_chunks:
        challenges.append(
            Challenge(
                challenge_id=str(uuid.uuid4())[:8],
                target_claim=answer[:80],
                objection=(
                    f"{len(low_conf_chunks)} of {len(evidence)} retrieved chunks have low "
                    f"fused relevance score (<0.25) — weak topical match to the question."
                ),
                severity=0.4,
                resolved=False,
            )
        )

    if not challenges:
        challenges.append(
            Challenge(
                challenge_id=str(uuid.uuid4())[:8],
                target_claim=answer[:80],
                objection=call_llm(CRITIC_SYSTEM, f"Q: {question}\nA: {answer}", seed=2),
                severity=0.2,
                resolved=False,
            )
        )

    return challenges


def run_fact_checker(answer: str, evidence: list[EvidenceChunk]) -> list[FactCheckResult]:
    results = []
    for e in evidence[:3]:  # fact-check top chunks; extend to all claims in real mode
        verdict = call_llm(FACT_CHECKER_SYSTEM, f"Claim: {answer[:120]}\nEvidence: {e.text}", seed=hash(e.chunk_id) % 1000)
        results.append(
            FactCheckResult(
                claim=answer[:120],
                supported=(verdict == "SUPPORTED"),
                supporting_evidence_ids=[e.chunk_id] if verdict == "SUPPORTED" else [],
                contradicting_evidence_ids=[e.chunk_id] if verdict == "CONTRADICTED" else [],
                notes=verdict,
            )
        )
    return results


def run_consensus(
    challenges: list[Challenge], fact_checks: list[FactCheckResult]
) -> tuple[float, str, str]:
    """
    Deterministic, auditable scoring function — NOT left to the LLM's vibes.
    This matters for the demo: judges can see exactly why confidence dropped.
    Real mode can still call the LLM for the rationale text, but the number
    itself should come from a rule you can defend on stage.
    """
    base = 0.9
    for c in challenges:
        if not c.resolved:
            base -= c.severity * 0.3

    contradicted = sum(1 for f in fact_checks if not f.supported and f.notes == "CONTRADICTED")
    insufficient = sum(1 for f in fact_checks if f.notes == "INSUFFICIENT_EVIDENCE")
    base -= contradicted * 0.35
    base -= insufficient * 0.1

    score = max(0.0, min(1.0, base))

    if contradicted:
        verdict = "refuted"
    elif score >= 0.75:
        verdict = "supported"
    elif score >= 0.4:
        verdict = "uncertain"
    else:
        verdict = "unverifiable"

    rationale = (
        f"Base confidence 0.90, reduced by {len(challenges)} challenge(s) "
        f"(unresolved severity sum {sum(c.severity for c in challenges if not c.resolved):.2f}), "
        f"{contradicted} contradicted fact-check(s), {insufficient} insufficient-evidence result(s)."
    )
    return score, verdict, rationale
