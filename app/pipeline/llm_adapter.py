"""
Single choke point for all LLM calls. Swap MODE to "openai" / "anthropic" /
"gemini" once you have API keys — nothing else in the pipeline changes,
because every agent only ever calls `call_llm(system, user)`.

Default MODE="mock" runs a fully offline, deterministic simulation so you
can develop/demo the pipeline (and grade the hash-chain logic, the graph,
the certificate) without spending API credits or needing network access.
Wire in a real provider the night before the demo — it's a ~15-line change.
"""

from __future__ import annotations

import os
import random

MODE = os.environ.get("VERIFAI_LLM_MODE", "mock")


def call_llm(system: str, user: str, seed: int | None = None) -> str:
    if MODE == "mock":
        return _mock_call(system, user, seed)
    elif MODE == "openai":
        return _openai_call(system, user)
    elif MODE == "anthropic":
        return _anthropic_call(system, user)
    else:
        raise ValueError(f"Unknown VERIFAI_LLM_MODE: {MODE}")


def _mock_call(system: str, user: str, seed: int | None) -> str:
    """
    Deterministic stand-in so the pipeline is testable/demoable offline.
    Real agents.py prompts are written so a real LLM slots in with no
    prompt changes — only this function's body needs replacing.
    """
    rng = random.Random(seed if seed is not None else hash(user) % (2**32))
    role = "GENERATOR" if "Generator" in system else \
           "CRITIC" if "Critic" in system else \
           "FACT_CHECKER" if "Fact" in system else "CONSENSUS"

    if role == "GENERATOR":
        return (
            "Based on the retrieved evidence, the most supported answer is "
            "derived directly from the highest-fused-score chunks. "
            "[MOCK GENERATOR OUTPUT — replace llm_adapter.MODE for a real model]"
        )
    if role == "CRITIC":
        objections = [
            "The evidence may be outdated relative to the question's timeframe.",
            "Only one source supports this claim; single-source claims are weaker.",
            "The retrieved chunk discusses a related but not identical entity.",
        ]
        return rng.choice(objections)
    if role == "FACT_CHECKER":
        return rng.choice(["SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"])
    return "CONSENSUS_OK"


def _openai_call(system: str, user: str) -> str:
    import openai  # pip install openai
    client = openai.OpenAI()
    resp = client.chat.completions.create(
        model=os.environ.get("VERIFAI_OPENAI_MODEL", "gpt-4o"),
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    return resp.choices[0].message.content


def _anthropic_call(system: str, user: str) -> str:
    import anthropic  # pip install anthropic
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=os.environ.get("VERIFAI_ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return resp.content[0].text
