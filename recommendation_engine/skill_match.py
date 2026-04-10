"""Skill overlap score in [0, 1]."""

from __future__ import annotations

from typing import Dict, List, Tuple


def skill_overlap_score(user_skills: List[str], project: Dict) -> Tuple[float, List[str]]:
    required = project.get("skills", [])
    if not isinstance(required, list):
        required = [str(required)]
    normalized_required = [s.strip().lower() for s in required if str(s).strip()]
    if not normalized_required:
        return 1.0, []

    user_set = set(s.strip().lower() for s in user_skills)
    matched = [s for s in normalized_required if s in user_set]
    score = len(matched) / len(normalized_required)
    return float(score), matched
