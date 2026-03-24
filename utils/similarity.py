from __future__ import annotations

import numpy as np


def cosine_similarity(query_embedding: np.ndarray, project_embeddings: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between query and project embeddings."""
    if query_embedding.ndim != 1:
        raise ValueError("query_embedding must be 1-dimensional")
    if project_embeddings.ndim != 2:
        raise ValueError("project_embeddings must be 2-dimensional")

    query_norm = np.linalg.norm(query_embedding)
    project_norms = np.linalg.norm(project_embeddings, axis=1)

    query_norm = np.where(query_norm == 0.0, 1e-12, query_norm)
    project_norms = np.where(project_norms == 0.0, 1e-12, project_norms)

    return np.dot(project_embeddings, query_embedding) / (project_norms * query_norm)
