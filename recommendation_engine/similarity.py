"""Cosine similarity over L2-normalized 384-d vectors (efficient dot products)."""

from __future__ import annotations

import numpy as np


def l2_normalize_rows(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    return matrix / norms


def l2_normalize_vector(vec: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(vec)
    if n < 1e-12:
        return vec
    return vec / n


def cosine_similarity_scores(query_embedding: np.ndarray, project_embeddings: np.ndarray) -> np.ndarray:
    """
    query_embedding: shape (384,)
    project_embeddings: shape (n, 384)
    returns: shape (n,) in [0, 1] when inputs are non-negative cosine from normalized dot
    """
    if query_embedding.ndim != 1:
        raise ValueError("query_embedding must be 1-d")
    if project_embeddings.ndim != 2:
        raise ValueError("project_embeddings must be 2-d")
    if project_embeddings.shape[0] == 0:
        return np.zeros((0,), dtype=np.float32)

    q = l2_normalize_vector(query_embedding.astype(np.float32))
    p = l2_normalize_rows(project_embeddings.astype(np.float32))
    sim = p @ q
    return np.clip(sim.astype(np.float32), 0.0, 1.0)
