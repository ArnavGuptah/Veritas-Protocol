from __future__ import annotations

import re


GENERATOR_PREFIX_RE = re.compile(
    r"^\s*"
    r"based\s+(?:strictly\s+)?on\s+the\s+retrieved\s+evidence"
    r"(?:\s*,\s*|\s*:\s*)"
    r"(?:the\s+available\s+source\s+states\s*:?\s*)?"
    r"\s*",
    flags=re.IGNORECASE,
)


def extract_claims(answer: str) -> list[str]:

    text = answer.strip()

    if not text:
        return []

    # --------------------------------------------------
    # 1. Remove generator wrapper
    # --------------------------------------------------

    text = GENERATOR_PREFIX_RE.sub(
        "",
        text,
        count=1,
    )

    # --------------------------------------------------
    # 2. Remove leading Yes/No wrapper
    # --------------------------------------------------

    text = re.sub(
        r"^\s*(?:yes|no)\.\s+",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # --------------------------------------------------
    # 3. Remove citation markers
    # --------------------------------------------------

    text = re.sub(
        r"\s*\[[^\]]+\]",
        "",
        text,
    )

    text = text.strip()

    if not text:
        return []

    # --------------------------------------------------
    # 4. Protect personal-name initials
    #
    # Example: John F. Clauser
    # We don't want "F." to become a sentence boundary.
    # --------------------------------------------------

    protected = {}

    def protect_initial(match: re.Match) -> str:
        token = f"__INITIAL_{len(protected)}__"
        protected[token] = match.group(0)
        return token

    text = re.sub(
        r"\b[A-Z]\.(?=\s+[A-Z][a-z])",
        protect_initial,
        text,
    )

    # --------------------------------------------------
    # 5. Split sentences
    # --------------------------------------------------

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    claims: list[str] = []

    for sentence in sentences:

        sentence = sentence.strip()

        # Restore initials.
        for token, original in protected.items():
            sentence = sentence.replace(
                token,
                original,
            )

        if len(sentence) < 15:
            continue

        claims.append(sentence)

    return claims