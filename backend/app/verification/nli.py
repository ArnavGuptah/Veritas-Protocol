from __future__ import annotations
from functools import lru_cache
from sentence_transformers import CrossEncoder
import numpy as np
from app.verification.relevance import semantic_similarity

MODEL_NAME = "cross-encoder/nli-deberta-v3-base"

@lru_cache(maxsize=1)
def get_model() -> CrossEncoder:
    model = CrossEncoder(
        MODEL_NAME,
        max_length=512,
    )

    print(
        "NLI LABEL MAP:",
        model.model.config.id2label
    )

    return model


def check_entailment(claim: str, evidence: str,) -> dict:

    relevance_score = semantic_similarity(
        claim,
        evidence,
    )

    print(f"[RELEVANCE] {relevance_score:.4f} | claim: {claim}")

    # Evidence is not sufficiently related to the claim.
    # Do NOT allow NLI to call this contradiction.
    if relevance_score < 0.0:

        print(
            "[NLI] neutral | evidence is not semantically relevant"
        )

        return {
            "label": "neutral",
            "scores": {
                "contradiction": 0.0,
                "entailment": 0.0,
                "neutral": 1.0,
            },
            "relevance_score": relevance_score,
        }

    # --------------------------------------------------
    # STEP 2: NLI
    # --------------------------------------------------

    model = get_model()

    # Evidence = premise
    # Claim = hypothesis

    logits = model.predict(
        [(evidence, claim)]
    )

    # Stable softmax
    probabilities = np.exp(
        logits[0] - np.max(logits[0])
    )

    probabilities = (
        probabilities /
        probabilities.sum()
    )

    labels = [
        "contradiction",
        "entailment",
        "neutral",
    ]

    result = {
        label: float(score)
        for label, score in zip(
            labels,
            probabilities,
        )
    }

    predicted = max(
        result,
        key=result.get,
    )

    print(
        "[NLI]",
        predicted,
        "| entailment:",
        round(result["entailment"], 4),
        "| contradiction:",
        round(result["contradiction"], 4),
        "| neutral:",
        round(result["neutral"], 4),
        "| relevance:",
        round(relevance_score, 4),
    )

    return {
        "label": predicted,
        "scores": result,
        "relevance_score": relevance_score,
    }