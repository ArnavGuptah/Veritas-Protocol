from __future__ import annotations
import re
from dataclasses import dataclass


STOPWORDS = {
    "what",
    "is",
    "are",
    "was",
    "were",
    "the",
    "a",
    "an",
    "of",
    "in",
    "on",
    "for",
    "to",
    "and",
    "or",
    "does",
    "do",
    "how",
    "why",
    "when",
    "where",
    "who",
}


@dataclass
class QueryAnalysis:
    original: str
    normalized: str
    tokens: list[str]
    keywords: list[str]


def analyze_query(question: str) -> QueryAnalysis:

    normalized = re.sub(
        r"\s+",
        " ",
        question.strip().lower(),
    )

    tokens = re.findall(
        r"[a-z0-9]+",
        normalized,
    )

    keywords = [
        token
        for token in tokens
        if token not in STOPWORDS
        and len(token) > 2
    ]

    return QueryAnalysis(
        original=question,
        normalized=normalized,
        tokens=tokens,
        keywords=keywords,
    )