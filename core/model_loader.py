from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from core.config import CONFIG


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load sentence-transformer once per process.
    Prefer local offline model path to avoid runtime network dependency.
    """
    if CONFIG.local_model_dir.exists():
        return SentenceTransformer(str(CONFIG.local_model_dir), local_files_only=True)
    return SentenceTransformer(CONFIG.model_name)
