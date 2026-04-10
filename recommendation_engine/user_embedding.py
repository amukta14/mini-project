"""Encode user profile (interests, skills, domains, project type) with sentence-transformers."""

from __future__ import annotations

import numpy as np

from core.model_loader import get_embedding_model
from services.preprocessing_service import ProcessedInput


def build_user_profile_text(user: ProcessedInput) -> str:
    """Structured narrative for embedding (not keyword stuffing)."""
    skills = ", ".join(user.skills) if user.skills else "general programming and analysis"
    domains = ", ".join(user.domain_preference) if user.domain_preference else "open-ended applied projects"
    sector = (getattr(user, "sector_context", None) or "").strip()
    sector_line = f"Target industry sector: {sector}." if sector else ""

    parts = [
        f"Interests and goals: {user.interests or 'build a strong capstone with measurable impact'}.",
        f"Core skills: {skills}.",
        f"Preferred domains: {domains}.",
    ]
    if sector_line:
        parts.append(sector_line)
    parts.extend(
        [
            f"Project shape: {user.preferred_project_type or 'balanced research and implementation'}.",
            f"Execution context: time horizon {user.time_available or 'medium'}, "
            f"experience {user.experience_level or 'intermediate'}, "
            f"hardware {user.hardware_availability or 'standard laptop'}.",
            f"Team style: {user.team_or_individual or 'flexible'}. "
            f"Learning vs delivery emphasis: {user.learning_vs_execution or 'balanced'}.",
        ]
    )
    return " ".join(parts)


def embed_user_profile(user: ProcessedInput) -> np.ndarray:
    model = get_embedding_model()
    text = build_user_profile_text(user)
    vec = model.encode(text, convert_to_numpy=True, normalize_embeddings=False)
    return vec.astype(np.float32).reshape(-1)
