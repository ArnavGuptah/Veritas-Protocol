from __future__ import annotations
import re

def extract_claims(answer: str) -> list[str]:

    text = answer.strip()

    if not text:
        return []

# Remove generator wrapper regardless of exact wording.

    text = re.sub(
        r"^based on the retrieved evidence,\s*"
        r"(?:the available source states:\s*)?",
        "",
        text,
        flags=re.IGNORECASE,
    )

# --------------------------------------------------
# Remove citation markers
# --------------------------------------------------

    text = re.sub(
        r"^based strictly on the retrieved evidence,\s*"
        r"(?:the available source states:\s*)?",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove citation markers.
    text = re.sub(
        r"\s*\[[^\]]+\]",
        "",
        text,
    ).strip()

    text = re.sub(
        r"\b([A-Z])\.",
        r"\1<INITIAL>",
        text,
    )

    # Split sentences.
    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    claims = []

    for sentence in sentences:

        sentence = sentence.replace(
            "<INITIAL>",
            ".",
        ).strip()

        if not sentence:
            continue

        if len(sentence) < 15:
            continue

        claims.append(sentence)

    return claims