from __future__ import annotations
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def semantic_similarity(
    claim: str,
    evidence: str,
) -> float:

    model = get_model()

    embeddings = model.encode(
        [claim, evidence],
        normalize_embeddings=True,
    )

    score = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]],
    )[0][0]

    return float(score)