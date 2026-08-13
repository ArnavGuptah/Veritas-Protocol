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
from app.pipeline.claims import extract_claims
from app.verification.nli import check_entailment


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

CLAIM_EXTRACTOR_SYSTEM = """You are the Claim Extraction agent.

Break the generator's answer into discrete factual claims.

Rules:
- Each claim must express exactly one independently verifiable fact.
- Do not merge multiple facts into one claim.
- Remove introductory phrases such as "Based on the evidence".
- Do not add information.
- Preserve the meaning of the original answer.
- Return ONLY a JSON array of strings.

Example:

Input:
"TB is an infectious disease caused by Mycobacterium tuberculosis.
It primarily affects the lungs."

Output:
[
  "Tuberculosis is an infectious disease.",
  "Tuberculosis is caused by Mycobacterium tuberculosis.",
  "Tuberculosis primarily affects the lungs."
]
"""


def run_generator(question: str, evidence: list[EvidenceChunk]) -> str:
    if not evidence:
        return (
            "Insufficient relevant evidence was retrieved "
            "to answer the submitted question."
        )

    evidence_block = "\n".join(
        f"[{e.chunk_id}] {e.text}"
        for e in evidence
    )

    user = (
        f"Question: {question}\n\n"
        f"Evidence:\n{evidence_block}"
    )

    return call_llm(GENERATOR_SYSTEM, user)


def run_critic(question: str, answer: str, evidence: list[EvidenceChunk]) -> list[Challenge]:
    """
    In mock mode this raises a bounded, evidence-aware set of challenges so
    the demo has something real to attack. In real mode, parse the LLM's
    structured objections (ask it for JSON) into Challenge objects the same
    way — the shape below is what your real prompt should target.
    """
    challenges: list[Challenge] = []

    if answer.lower().startswith(
        "insufficient relevant evidence was retrieved"
    ):
        return []

# --------------------------------------------------
# 0. No evidence = major verification failure
# --------------------------------------------------

    if not evidence:
        challenges.append(
            Challenge(
                challenge_id=str(uuid.uuid4())[:8],
                target_claim=answer[:120],
                objection=(
                    "No retrieved evidence is available to substantiate "
                    "the generator's answer."
                ),
                severity=0.8,
                resolved=False,
            )
        )

        return challenges

    # Heuristic + LLM-flavored challenge: single-source claims are always
    # worth flagging regardless of model quality — a good adversarial system
    # doesn't rely on the LLM to remember this every time.

    sources = {e.source for e in evidence}

    if len(sources) <= 1 and evidence:
        challenges.append(
            Challenge(
                challenge_id=str(uuid.uuid4())[:8],
                target_claim=answer[:80],
                objection=call_llm(
                    CRITIC_SYSTEM,
                    f"Q: {question}\nA: {answer}\nEvidence sources: {sources}",
                    seed=1
                ),
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
                    f"{len(low_conf_chunks)} of {len(evidence)}"
                    "retrieved chunks have low fused relevance"
                    f"fused relevance score (<0.25) — weak topical match to the question."
                ),
                severity=0.4,
                resolved=False,
            )
        )
# --------------------------------------------------
# 3. Generic claim-evidence support check
# --------------------------------------------------

    claims = extract_claims(answer)

    for claim in claims:

        best_entailment = 0.0
        best_supporting_chunk = None

        for e in evidence:

            # Ignore weak retrieval results.
            if e.fused_score < 0.25:
                continue

            nli = check_entailment(
                claim,
                e.text,
            )

            entailment_score = nli["scores"].get(
                "entailment",
                0.0,
            )

            if entailment_score > best_entailment:
                best_entailment = entailment_score
                best_supporting_chunk = e.chunk_id

        # No sufficiently strong evidence supports this claim.
        if best_entailment < 0.70:

            challenges.append(
                Challenge(
                    challenge_id=str(uuid.uuid4())[:8],
                    target_claim=claim[:120],
                    objection=(
                        f"Claim lacks strong direct evidence support. "
                        f"Best entailment score was "
                        f"{best_entailment:.3f}"
                        + (
                            f" from {best_supporting_chunk}."
                            if best_supporting_chunk
                            else "."
                        )
                    ),
                    severity=0.5,
                    resolved=False,
                )
            )

    
# --------------------------------------------------
# 4. No problems found
# --------------------------------------------------

    if not challenges:
        challenges.append(
            Challenge(
                challenge_id=str(uuid.uuid4())[:8],
                target_claim=answer[:80],
                objection=(
                    "No material contradiction or unsupported claim "
                    "was identified in the retrieved evidence."
                ),
                severity=0.0,
                resolved=True,
                resolution_note="No actionable challenge identified.",
            )
        )

    return challenges

def run_fact_checker(answer: str, evidence: list[EvidenceChunk]) -> list[FactCheckResult]:

    if answer.lower().startswith(
        "insufficient relevant evidence was retrieved"
    ):
        return []

    claims = extract_claims(answer)

    print("\n========== CLAIM DECOMPOSITION ==========")

    for i, claim in enumerate(claims, 1):
        print(f"{i}. {claim}")

    print("=========================================\n")

    if not evidence:
        return [
            FactCheckResult(
                claim=claim,
                supported=False,
                supporting_evidence_ids=[],
                contradicting_evidence_ids=[],
                notes="INSUFFICIENT_EVIDENCE",
            )
            for claim in claims
        ]

    results: list[FactCheckResult] = []

    for claim in claims:

        best_entailment = 0.0
        best_entailing_id = None

        best_contradiction = 0.0
        best_contradicting_id = None

        print(f"\n[FACT CHECK] CLAIM: {claim}")

        for e in evidence:

            result = check_entailment(
                claim,
                e.text,
            )

            relevance = result.get("relevance_score", 0.0)

            entailment = result["scores"].get(
                "entailment",
                0.0,
            )

            contradiction = result["scores"].get(
                "contradiction",
                0.0,
            )

            print(
                f"  {e.chunk_id} | "
                f"relevance={relevance:.3f} | "
                f"entailment={entailment:.3f} | "
                f"contradiction={contradiction:.3f}"
            )

            # Ignore semantically unrelated evidence.
            if relevance < 0.20:
                continue

            if entailment > best_entailment:
                best_entailment = entailment
                best_entailing_id = e.chunk_id

            if contradiction > best_contradiction:
                best_contradiction = contradiction
                best_contradicting_id = e.chunk_id

        # --------------------------------------------------
        # CONTRADICTION HAS ABSOLUTE PRIORITY
        # --------------------------------------------------

        if best_contradiction >= 0.70:

            results.append(
                FactCheckResult(
                    claim=claim,
                    supported=False,
                    supporting_evidence_ids=[],
                    contradicting_evidence_ids=[
                        best_contradicting_id
                    ],
                    notes="CONTRADICTED",
                )
            )

            continue

        # --------------------------------------------------
        # STRONG ENTAILMENT
        # --------------------------------------------------

        if best_entailment >= 0.80:

            results.append(
                FactCheckResult(
                    claim=claim,
                    supported=True,
                    supporting_evidence_ids=[
                        best_entailing_id
                    ],
                    contradicting_evidence_ids=[],
                    notes="SUPPORTED",
                )
            )

            continue

        # --------------------------------------------------
        # EVERYTHING ELSE
        # --------------------------------------------------

        results.append(
            FactCheckResult(
                claim=claim,
                supported=False,
                supporting_evidence_ids=[],
                contradicting_evidence_ids=[],
                notes="INSUFFICIENT_EVIDENCE",
            )
        )

    return results

def run_consensus(challenges: list[Challenge], fact_checks: list[FactCheckResult], evidence: list[EvidenceChunk]) -> tuple[float, str, str]:
    """
    Deterministic, auditable scoring function — NOT left to the LLM's vibes.
    This matters for the demo: judges can see exactly why confidence dropped.
    Real mode can still call the LLM for the rationale text, but the number
    itself should come from a rule you can defend on stage.
    """
    if not fact_checks:
        return (
            0.0,
            "unverifiable",
            "No fact-check results were produced.",
        )

    contradicted = sum(
        1
        for f in fact_checks
        if f.notes == "CONTRADICTED"
    )

    insufficient = sum(
        1
        for f in fact_checks
        if f.notes == "INSUFFICIENT_EVIDENCE"
    )

    supported = sum(
        1
        for f in fact_checks
        if f.notes == "SUPPORTED"
    )

    total = len(fact_checks)

    # -------------------------------------------------
    # HARD SAFETY RULE
    # -------------------------------------------------

    if contradicted > 0:

        score = 0.05
        verdict = "refuted"

    elif supported == 0:

        score = 0.15
        verdict = "unverifiable"

    else:

        claim_ratio = supported / total

        # Unique source count among supporting evidence
        source_map = {
            e.chunk_id: e.source
            for e in evidence
        }

        supporting_sources = set()

        for fact_check in fact_checks:

            if fact_check.notes != "SUPPORTED":
                continue

            for evidence_id in fact_check.supporting_evidence_ids:

                source = source_map.get(evidence_id)

                if source:
                    supporting_sources.add(source)

        source_count = len(supporting_sources)

        # Diversity bonus
        if source_count >= 3:
            diversity_bonus = 0.10

        elif source_count == 2:
            diversity_bonus = 0.07

        elif source_count == 1:
            diversity_bonus = 0.02

        else:
            diversity_bonus = 0.0

        score = (
            0.65
            + (0.25 * claim_ratio)
            + diversity_bonus
        )

        unresolved_severity = sum(
            c.severity
            for c in challenges
            if not c.resolved
        )

        score -= min(
            unresolved_severity * 0.10,
            0.20,
        )

        score = max(
            0.0,
            min(1.0, score),
        )

        if score >= 0.85:
            verdict = "supported"

        elif score >= 0.50:
            verdict = "uncertain"

        else:
            verdict = "unverifiable"

    rationale = (
        f"{supported} supported, "
        f"{contradicted} contradicted, "
        f"{insufficient} insufficient-evidence "
        f"claim(s)."
    )

    return score, verdict, rationale