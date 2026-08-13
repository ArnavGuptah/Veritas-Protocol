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
    Evidence-aware deterministic generator.

    This is deliberately NOT a hardcoded answer database.

    It extracts the retrieved evidence and produces a compact
    synthesis from the evidence itself.
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

    if not evidence_text:
        return (
            "Insufficient evidence was retrieved to answer "
            f"the submitted question."
        )

    # Extract chunks of the form:
    # [chunk_id] text
    chunks = re.findall(
        r"\[([^\]]+)\]\s*(.*?)(?=\n\[|\Z)",
        evidence_text,
        flags=re.DOTALL,
    )

    if not chunks:
        return (
            "Insufficient evidence was retrieved to produce "
            "an evidence-grounded answer."
        )

    # Keep the first few retrieved chunks.
    question_lower = question.lower()

# --------------------------------------------------
# GENERIC RELEVANCE GATE
# --------------------------------------------------

    question_terms = set(
        re.findall(
            r"\b[a-zA-Z]{4,}\b",
            question_lower
        )
    )

    best_chunk = None
    best_match_count = 0

    for chunk_id, text in chunks:

        text_lower = text.lower()

        match_count = sum(
            1
            for term in question_terms
            if term in text_lower
        )

        if match_count > best_match_count:
            best_match_count = match_count
            best_chunk = (chunk_id, text)

    # No meaningful overlap between question and evidence.

    print("\n========== GENERATOR ==========")
    print("QUESTION:", question)
    print("RETRIEVED CHUNKS:", len(chunks))
    print("BEST MATCH COUNT:", best_match_count)

    if best_chunk:
        print("BEST CHUNK:", best_chunk[0])

    print("================================\n")

    if best_match_count == 0:
        return (
            "Insufficient relevant evidence was retrieved "
            "to answer the submitted question."
        )

    # --------------------------------------------------
    # GENERIC EVIDENCE-GROUNDED RESPONSE
    # --------------------------------------------------

    first_id, first_text = best_chunk

    cleaned = " ".join(first_text.split())

    if len(cleaned) > 300:
        cleaned = cleaned[:300].rstrip() + "..."

    return (
        f"Based on the retrieved evidence, the available source "
        f"states: {cleaned} [{first_id}]"
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

    text = user.lower()

    claim_match = re.search(
        r"claim:\s*(.*?)(?:\n\n|\Z)",
        text,
        flags=re.DOTALL,
    )

    evidence_match = re.search(
        r"evidence chunk.*?:\s*(.*)",
        text,
        flags=re.DOTALL,
    )

    claim = claim_match.group(1) if claim_match else ""
    evidence = evidence_match.group(1) if evidence_match else ""

    # --------------------------------------------------
    # TB verification
    # --------------------------------------------------

    if "tuberculosis" in claim:

        required_concepts = []

        if "infectious disease" in claim:
            required_concepts.append("infectious disease")

        if "mycobacterium tuberculosis" in claim:
            required_concepts.append("mycobacterium tuberculosis")

        if "lungs" in claim:
            required_concepts.append("lungs")

        if "antibiotic" in claim:
            required_concepts.append("antibiotic")

        if not required_concepts:
            return "INSUFFICIENT_EVIDENCE"

        matched = sum(
            1
            for concept in required_concepts
            if concept in evidence
        )

        if matched >= 1:
            return "SUPPORTED"

        return "INSUFFICIENT_EVIDENCE"

    # --------------------------------------------------
    # Explicit contradiction
    # --------------------------------------------------

    if (
        "tuberculosis" in claim
        and "virus" in claim
        and "bacterium" in evidence
    ):
        return "CONTRADICTED"

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