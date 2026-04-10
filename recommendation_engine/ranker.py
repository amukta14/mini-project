"""Weighted scoring + diversity selection for top-k recommendations."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

from services.preprocessing_service import ProcessedInput

from core.config import CONFIG
from recommendation_engine.feasibility import compute_feasibility
from recommendation_engine.similarity import cosine_similarity_scores
from recommendation_engine.skill_match import skill_overlap_score
from recommendation_engine.user_embedding import embed_user_profile


@dataclass
class ScoredProject:
    project: Dict
    semantic_score: float
    skill_score: float
    feasibility_score: float
    final_score: float
    matched_skills: List[str]
    feasibility_notes: List[str]


def _bucket(project: Dict) -> Tuple[str, str]:
    slug = str(project.get("sector_slug") or "").strip().lower()
    if not slug:
        s = str(project.get("sector") or "").strip().lower()
        slug = re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "general"
    hint = str(project.get("archetype_hint") or "").strip().lower()
    return slug, hint


def select_diverse(scored: List[ScoredProject], k: int, max_per_bucket: int = 2) -> List[ScoredProject]:
    selected: List[ScoredProject] = []
    seen_titles: set[str] = set()

    def count_bucket(key: Tuple[str, str]) -> int:
        return sum(1 for s in selected if _bucket(s.project) == key)

    for item in scored:
        if len(selected) >= k:
            break
        title = str(item.project.get("title") or "").strip()
        if not title or title in seen_titles:
            continue
        key = _bucket(item.project)
        if count_bucket(key) >= max_per_bucket:
            continue
        selected.append(item)
        seen_titles.add(title)

    for item in scored:
        if len(selected) >= k:
            break
        title = str(item.project.get("title") or "").strip()
        if not title or title in seen_titles:
            continue
        selected.append(item)
        seen_titles.add(title)

    return selected[:k]


def score_and_rank(
    user: ProcessedInput,
    projects: List[Dict],
    project_embeddings: np.ndarray,
    top_k: int,
) -> List[ScoredProject]:
    w = CONFIG.ranking_weights
    if not projects:
        return []

    user_vec = embed_user_profile(user)
    sem = cosine_similarity_scores(user_vec, project_embeddings)

    scored: List[ScoredProject] = []
    for i, project in enumerate(projects):
        sk, matched = skill_overlap_score(user.skills, project)
        fe, fe_notes = compute_feasibility(user, project)
        final = (w.semantic * float(sem[i])) + (w.skill * sk) + (w.feasibility * fe)
        final = float(max(0.0, min(1.0, final)))
        scored.append(
            ScoredProject(
                project=project,
                semantic_score=float(sem[i]),
                skill_score=sk,
                feasibility_score=fe,
                final_score=final,
                matched_skills=matched,
                feasibility_notes=fe_notes,
            )
        )

    scored.sort(key=lambda x: x.final_score, reverse=True)
    return select_diverse(scored, top_k, max_per_bucket=2)
