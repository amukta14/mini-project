from __future__ import annotations

import numpy as np


def cosine_similarity_scores(query_embedding: np.ndarray, project_embeddings: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarity between one query embedding and all project embeddings.
    Returns scores in [0, 1] via normalization from cosine [-1, 1].
    """
    if query_embedding.ndim != 1:
        raise ValueError("query_embedding must be 1-dimensional")
    if project_embeddings.ndim != 2:
        raise ValueError("project_embeddings must be 2-dimensional")
    if project_embeddings.shape[0] == 0:
        return np.array([], dtype=np.float32)

    q_norm = np.linalg.norm(query_embedding)
    p_norms = np.linalg.norm(project_embeddings, axis=1)
    q_norm = max(float(q_norm), 1e-12)
    p_norms = np.where(p_norms == 0.0, 1e-12, p_norms)

    cos = np.dot(project_embeddings, query_embedding) / (p_norms * q_norm)
    cos = np.clip(cos, -1.0, 1.0)
    return ((cos + 1.0) / 2.0).astype(np.float32)
