"""
Feature 1: Verifiable RAG.

Hybrid retrieval = BM25 (lexical) + TF-IDF cosine (semantic-ish, no GPU/API
needed) fused by weighted sum. Swap `TfidfVectorizer` for a real embedding
model (bge-large / text-embedding-3-large) in production — the interface
below (`Retriever.search`) doesn't need to change.

Every returned chunk carries source, similarity, bm25 score, fused score,
and a document hash — so nothing is retrieved without a trace back to
where it came from. That traceability is the entire point of Feature 1;
a plain top-k vector search would not satisfy it.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.proof_object import EvidenceChunk


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _doc_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


@dataclass
class Document:
    doc_id: str
    source: str
    text: str


class Retriever:
    """
    In production, replace `documents` with your Qdrant/Chroma-backed corpus
    and swap TF-IDF for real embeddings. Chunking is naive (paragraph split)
    on purpose — this is a reference implementation, not the demo bottleneck.
    """

    def __init__(self, documents: list[Document]):
        self.chunks: list[EvidenceChunk] = []
        self._raw_texts: list[str] = []

        for doc in documents:
            for i, para in enumerate(p.strip() for p in doc.text.split("\n\n")):
                if not para:
                    continue
                chunk_id = f"{doc.doc_id}::chunk{i}"
                self.chunks.append(
                    EvidenceChunk(
                        chunk_id=chunk_id,
                        text=para,
                        source=doc.source,
                        similarity=0.0,
                        bm25_score=0.0,
                        fused_score=0.0,
                        document_hash=_doc_hash(doc.text),
                    )
                )
                self._raw_texts.append(para)

        tokenized = [_tokenize(t) for t in self._raw_texts]
        self._bm25 = BM25Okapi(tokenized) if tokenized else None

        self._tfidf = TfidfVectorizer()
        self._tfidf_matrix = (
            self._tfidf.fit_transform(self._raw_texts) if self._raw_texts else None
        )

    def search(self, query: str, top_k: int = 5, bm25_weight: float = 0.5) -> list[EvidenceChunk]:
        if not self.chunks:
            return []

        bm25_scores = self._bm25.get_scores(_tokenize(query))
        max_bm25 = max(bm25_scores) or 1.0

        query_vec = self._tfidf.transform([query])
        sim_scores = cosine_similarity(query_vec, self._tfidf_matrix)[0]

        scored: list[EvidenceChunk] = []
        for i, chunk in enumerate(self.chunks):
            bm25_norm = bm25_scores[i] / max_bm25
            sim = float(sim_scores[i])
            fused = bm25_weight * bm25_norm + (1 - bm25_weight) * sim
            scored.append(
                chunk.model_copy(
                    update={
                        "similarity": round(sim, 4),
                        "bm25_score": round(float(bm25_scores[i]), 4),
                        "fused_score": round(float(fused), 4),
                    }
                )
            )

        scored.sort(key=lambda c: c.fused_score, reverse=True)
        return scored[:top_k]
