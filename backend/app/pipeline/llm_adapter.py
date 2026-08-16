"""
Single choke point for all LLM calls.

MODE:
- mock      -> deterministic offline demo mode
- openai    -> OpenAI API
- anthropic -> Anthropic API

The rest of the verification pipeline only calls:
    call_llm(system, user)
"""

from __future__ import annotations
import re
import hashlib
import os
import random
from app.verification.relevance import semantic_similarity
from app.verification.nli import check_entailment
from dotenv import load_dotenv

load_dotenv()


MODE = os.environ.get("VERIFAI_LLM_MODE", "mock").lower()


def call_llm(system: str, user: str, seed: int | None = None) -> str:

    if MODE == "mock":
        return _mock_call(system, user, seed)

    if MODE == "openai":
        return _openai_call(system, user)

    if MODE == "anthropic":
        return _anthropic_call(system, user)

    raise ValueError(
        f"Unknown VERIFAI_LLM_MODE: {MODE}"
    )


# ============================================================
# MOCK MODE
# ============================================================

def _mock_call(system: str, user: str, seed: int | None = None,) -> str:

    system_lower = system.lower()
    user_lower = user.lower()

    # Stable seed. Do not use Python's hash() because it changes
    # between interpreter processes.

    if seed is None:
        seed_bytes = user.encode("utf-8")
        seed = int.from_bytes(
            hashlib.sha256(seed_bytes).digest()[:4],
            "big",
        )

    rng = random.Random(seed)

    # --------------------------------------------------------
    # CONSENSUS
    # --------------------------------------------------------

    if "you are the consensus agent" in system_lower:
        return "CONSENSUS_OK"

    # --------------------------------------------------------
    # CRITIC
    # --------------------------------------------------------

    if "you are the critic agent" in system_lower:
            return _mock_critic(user, rng)

    # --------------------------------------------------------
    # GENERATOR
    # --------------------------------------------------------

    if "you are the generator agent" in system_lower:
        return _mock_generate(user)

    # --------------------------------------------------------
    # FACT CHECKER
    # --------------------------------------------------------

    if "you are the fact checker agent" in system_lower:
        return _mock_fact_check(user)

    # --------------------------------------------------------
    # CLAIM EXTRACTION
    # --------------------------------------------------------

    if "you are the claim extraction agent" in system_lower:
        return _mock_extract_claims(user)

    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    return "CONSENSUS_OK"


# ============================================================
# OPENAI
# ============================================================

def _mock_generate(user: str) -> str:
    """
    Deterministic evidence-grounded generator.

    The generator must answer the QUESTION, not merely repeat
    the most topically similar evidence chunk.
    """

    question_match = re.search(
        r"Question:\s*(.*?)\n\nEvidence:",
        user,
        flags=re.IGNORECASE | re.DOTALL,
    )

    evidence_match = re.search(
        r"Evidence:\s*(.*)",
        user,
        flags=re.IGNORECASE | re.DOTALL,
    )

    question = (
        question_match.group(1).strip()
        if question_match
        else ""
    )

    evidence_text = (
        evidence_match.group(1).strip()
        if evidence_match
        else ""
    )

    if not question or not evidence_text:
        return (
            "Insufficient relevant evidence was retrieved "
            "to answer the submitted question."
        )

    chunks = re.findall(
        r"\[([^\]]+)\]\s*(.*?)(?=\n\[|\Z)",
        evidence_text,
        flags=re.DOTALL,
    )

    if not chunks:
        return (
            "Insufficient relevant evidence was retrieved "
            "to answer the submitted question."
        )

    print("\n========== GENERATOR ==========")
    print("QUESTION:", question)
    print("RETRIEVED CHUNKS:", len(chunks))

    # --------------------------------------------------
    # STEP 1: Rank evidence semantically
    # --------------------------------------------------

    ranked = []

    for chunk_id, text in chunks:

        similarity = semantic_similarity(
            question,
            text,
        )

        ranked.append(
            (
                similarity,
                chunk_id,
                text,
            )
        )

        print(
            f"{chunk_id} | semantic similarity={similarity:.4f}"
        )

    ranked.sort(
        key=lambda x: x[0],
        reverse=True,
    )

    # Only consider genuinely relevant evidence.
    relevant = [
        item
        for item in ranked
        if item[0] >= 0.20
    ]

    if not relevant:
        print("No semantically relevant evidence.")
        print("================================\n")

        return (
            "Insufficient relevant evidence was retrieved "
            "to answer the submitted question."
        )

    # --------------------------------------------------
    # STEP 2: Determine whether evidence supports,
    # contradicts, or does not answer the question.
    # --------------------------------------------------

    best_similarity, best_id, best_text = relevant[0]

    question_lower = question.lower()

    # Yes/no question detection.
    yes_no_question = bool(
        re.match(
            r"^(is|are|was|were|do|does|did|can|could|will|would|has|have|had)\b",
            question_lower,
        )
    )

    if yes_no_question:

        nli = check_entailment(question, best_text)

        entailment = nli["scores"]["entailment"]
        contradiction = nli["scores"]["contradiction"]

        print(
            "QUESTION NLI:",
            nli["label"],
            "| entailment:",
            round(entailment, 4),
            "| contradiction:",
            round(contradiction, 4),
        )

        if contradiction >= 0.70:

            # Evidence contradicts the proposition asked by
            # the user. Therefore the answer is "No".
            cleaned = " ".join(best_text.split())

            print("QUESTION IS CONTRADICTED BY EVIDENCE.")
            print("================================\n")

            return (
                f"No. The retrieved evidence states: "
                f"{cleaned} [{best_id}]"
            )

        if entailment >= 0.70:

            cleaned = " ".join(best_text.split())

            print("QUESTION IS SUPPORTED BY EVIDENCE.")
            print("================================\n")

            return (
                f"Yes. The retrieved evidence states: "
                f"{cleaned} [{best_id}]"
            )

# --------------------------------------------------
# STEP 3: Normal factual question
# --------------------------------------------------

    selected = relevant[:3]

    if not selected:
        return (
            "Insufficient relevant evidence was retrieved "
            "to answer the submitted question."
        )

    # Prefer the single most relevant chunk for the MVP mock.
    best_similarity, best_id, best_text = selected[0]

    cleaned = " ".join(best_text.split())

    if len(cleaned) > 400:
        cleaned = cleaned[:400].rstrip() + "..."

    print("BEST CHUNK:", best_id)
    print("BEST SIMILARITY:", round(best_similarity, 4))
    print("================================\n")

    return (
        f"Based strictly on the retrieved evidence: "
        f"{cleaned} [{best_id}]"
    )

# ============================================================
# MOCK CRITIC
# ============================================================

def _mock_critic(user: str, rng: random.Random) -> str:

    user_lower = user.lower()

    # No evidence = major problem.
    if "evidence sources:" not in user_lower:
        return (
            "No retrieved evidence is available to substantiate "
            "the generator's answer."
        )

    if "evidence sources: set()" in user_lower:
        return (
            "No retrieved evidence is available to substantiate "
            "the generator's answer."
        )

    objections = [
        (
            "Check whether every factual claim in the answer "
            "is directly supported by the retrieved evidence."
        ),
        (
            "The answer should distinguish directly supported "
            "claims from conclusions that require additional evidence."
        ),
        (
            "Multiple sources should be preferred where available "
            "to reduce dependence on a single evidence source."
        ),
        (
            "The retrieved evidence should be checked for relevance "
            "to the exact question rather than merely topical similarity."
        ),
    ]

    return rng.choice(objections)


# ============================================================
# MOCK FACT CHECKER
# ============================================================

def _mock_fact_check(user: str) -> str:
    """
    Generic deterministic fallback fact-checker.

    IMPORTANT:
    This function must never contain domain-specific knowledge.
    Actual semantic verification is handled by the NLI verifier.
    """

    text = user.strip()

    if not text:
        return "INSUFFICIENT_EVIDENCE"

    claim_match = re.search(
        r"claim:\s*(.*?)(?:\n\n|\Z)",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    evidence_match = re.search(
        r"evidence(?:\s+chunk)?(?:s| sources)?\s*:\s*(.*)",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    claim = claim_match.group(1).strip() if claim_match else ""
    evidence = evidence_match.group(1).strip() if evidence_match else ""

    if not claim or not evidence:
        return "INSUFFICIENT_EVIDENCE"

    # Conservative lexical fallback only.
    # This is NOT semantic verification.
    claim_terms = set(
        re.findall(
            r"\b[a-zA-Z]{4,}\b",
            claim.lower(),
        )
    )

    evidence_terms = set(
        re.findall(
            r"\b[a-zA-Z]{4,}\b",
            evidence.lower(),
        )
    )

    if not claim_terms:
        return "INSUFFICIENT_EVIDENCE"

    overlap = len(claim_terms & evidence_terms) / len(claim_terms)

    if overlap >= 0.70:
        return "SUPPORTED"

    return "INSUFFICIENT_EVIDENCE"

# ============================================================
# OPENAI
# ============================================================

def _openai_call(system: str, user: str,) -> str:

    import openai

    client = openai.OpenAI()

    response = client.chat.completions.create(
        model=os.environ.get(
            "VERIFAI_OPENAI_MODEL",
            "gpt-4o",
        ),
        messages=[
            {
                "role": "system",
                "content": system,
            },
            {
                "role": "user",
                "content": user,
            },
        ],
    )

    return response.choices[0].message.content or ""


# ============================================================
# ANTHROPIC
# ============================================================

def _anthropic_call(system: str, user: str,) -> str:

    import anthropic

    client = anthropic.Anthropic()

    response = client.messages.create(
        model=os.environ.get(
            "VERIFAI_ANTHROPIC_MODEL",
            "claude-sonnet-4-6",
        ),
        max_tokens=1024,
        system=system,
        messages=[
            {
                "role": "user",
                "content": user,
            }
        ],
    )

    return response.content[0].text

def _mock_extract_claims(user: str) -> str:

    sentences = re.split(
        r"(?<=[.!?])\s+",
        user.strip(),
    )

    claims = []

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        if sentence.startswith("["):
            continue

        if sentence.lower().startswith(
            "based on the retrieved evidence"
        ):
            continue

        claims.append(sentence)

    import json

    return json.dumps(claims)