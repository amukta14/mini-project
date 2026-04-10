"""End-to-end recommendation: score → diversify → generate project ideas."""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from core.config import CONFIG
from services.preprocessing_service import ProcessedInput

from recommendation_engine.generator import generate_recommendation
from recommendation_engine.ranker import score_and_rank


def run_recommendation_pipeline(
    user_input: ProcessedInput,
    projects: List[Dict[str, Any]],
    project_embeddings: np.ndarray,
) -> List[Dict[str, Any]]:
    if len(projects) != len(project_embeddings):
        raise ValueError("projects and embeddings length mismatch")

    scored = score_and_rank(user_input, projects, project_embeddings, CONFIG.top_k)
    used_titles: set[str] = set()
    return [generate_recommendation(sp, user_input, i, used_titles) for i, sp in enumerate(scored)]
