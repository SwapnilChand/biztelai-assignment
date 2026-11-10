"""Hybrid retrieval: BM25 for exact codes (AL-104, BH-220, SF-12) plus dense
embeddings for paraphrases ("who can take off a lock" vs "removing locks").

Both run fully on the laptop. Embeddings use fastembed (ONNX, CPU), so there is
no PyTorch and no external embedding API.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
from fastembed import TextEmbedding
from rank_bm25 import BM25Okapi

from .ingest import Chunk

EMBED_MODEL = "BAAI/bge-small-en-v1.5"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
RRF_K = 60


def tokenize(text: str) -> list[str]:
    # keep codes like al-104, bh-220, qc-sop-014 as single tokens
    return re.findall(r"[a-z0-9]+(?:[-./][a-z0-9]+)*", text.lower())


@dataclass
class Hit:
    chunk: Chunk
    score: float  # fused rank score, only meaningful for ordering
    cosine: float  # dense similarity, used for the "not in the documents" gate
    bm25: float


class Retriever:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self.model = TextEmbedding(EMBED_MODEL)
        self.vectors = np.array(list(self.model.embed([c.search_text for c in chunks])))
        self.vectors /= np.linalg.norm(self.vectors, axis=1, keepdims=True)
        self.bm25 = BM25Okapi([tokenize(c.search_text) for c in chunks])

    def search(self, query: str) -> list[Hit]:
        """Score every chunk (the corpus is small) and return them best first."""
        qv = np.array(list(self.model.embed([QUERY_PREFIX + query])))[0]
        qv /= np.linalg.norm(qv)
        cos = self.vectors @ qv
        bm = np.array(self.bm25.get_scores(tokenize(query)))

        dense_rank = {i: r for r, i in enumerate(np.argsort(-cos))}
        sparse_rank = {i: r for r, i in enumerate(np.argsort(-bm))}
        hits = []
        for i, c in enumerate(self.chunks):
            fused = 1 / (RRF_K + dense_rank[i])
            if bm[i] > 0:  # a chunk with zero keyword overlap gets no sparse vote
                fused += 1 / (RRF_K + sparse_rank[i])
            hits.append(Hit(c, fused, float(cos[i]), float(bm[i])))
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits
