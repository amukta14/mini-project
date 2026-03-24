from __future__ import annotations

import numpy as np

from core.model_loader import get_embedding_model


def create_query_embedding(query: str) -> np.ndarray:
    """Generate 384-d embedding from sentence-transformer."""
    if not query:
        return np.zeros((384,), dtype=np.float32)

    model = get_embedding_model()
    embedding = model.encode(query, convert_to_numpy=True, normalize_embeddings=False)
    return embedding.astype(np.float32)
