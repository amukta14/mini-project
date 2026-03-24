from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

from core.config import CONFIG
from services.project_idea_service import build_project_recommendation
from services.preprocessing_service import ProcessedInput
from services.similarity_service import cosine_similarity_scores


DIFFICULTY_ORDER = {"beginner": 1, "intermediate": 2, "advanced": 3}
PROJECT_DIFFICULTY_ORDER = {"easy": 1, "beginner": 1, "medium": 2, "intermediate": 2, "hard": 3, "advanced": 3}
TIME_COMPLEXITY_ORDER = {"short": 1, "medium": 2, "long": 3}
PROJECT_COMPLEXITY_ORDER = {"short": 1, "small": 1, "medium": 2, "moderate": 2, "long": 3, "complex": 3, "high": 3}


@dataclass
class ScoredProject:
    project: Dict
    semantic_similarity: float
    skill_match_score: float
    feasibility_score: float
    score: float
    matched_skills: List[str]


def compute_skill_match(user_skills: List[str], required_skills: List[str]) -> Tuple[float, List[str]]:
    normalized_required = [s.strip().lower() for s in required_skills if s]
    if not normalized_required:
        return 1.0, []

    user_skill_set = set(user_skills)
    matched = [skill for skill in normalized_required if skill in user_skill_set]
    score = len(matched) / len(normalized_required)
    return float(score), matched


def compute_feasibility_score(user_input: ProcessedInput, project: Dict) -> float:
    project_difficulty = str(project.get("difficulty", "intermediate")).lower().strip()
    project_complexity = str(project.get("complexity", "medium")).lower().strip()

    score = 1.0
    user_exp = user_input.experience_level or "intermediate"
    user_time = user_input.time_available or "medium"

    exp_idx = DIFFICULTY_ORDER.get(user_exp, 2)
    difficulty_idx = PROJECT_DIFFICULTY_ORDER.get(project_difficulty, 2)
    if exp_idx < difficulty_idx:
        gap = difficulty_idx - exp_idx
        score -= 0.35 if gap >= 2 else 0.2

    time_idx = TIME_COMPLEXITY_ORDER.get(user_time, 2)
    complexity_idx = PROJECT_COMPLEXITY_ORDER.get(project_complexity, 2)
    if time_idx < complexity_idx:
        gap = complexity_idx - time_idx
        score -= 0.3 if gap >= 2 else 0.15

    return float(max(0.0, min(1.0, score)))


def rank_projects(
    user_input: ProcessedInput,
    query_embedding: np.ndarray,
    projects: List[Dict],
    project_embeddings: np.ndarray,
) -> List[Dict]:
    if not projects:
        return []

    weights = CONFIG.ranking_weights.as_dict()
    semantic_scores = cosine_similarity_scores(query_embedding, project_embeddings)

    scored: List[ScoredProject] = []
    for idx, project in enumerate(projects):
        required_skills = project.get("skills", [])
        skill_score, matched_skills = compute_skill_match(user_input.skills, required_skills)
        feasibility_score = compute_feasibility_score(user_input, project)
        semantic_similarity = float(np.clip(semantic_scores[idx], 0.0, 1.0))
        final_score = (
            (weights["semantic"] * semantic_similarity)
            + (weights["skill"] * skill_score)
            + (weights["feasibility"] * feasibility_score)
        )
        final_score = float(max(0.0, min(1.0, final_score)))
        scored.append(
            ScoredProject(
                project=project,
                semantic_similarity=semantic_similarity,
                skill_match_score=skill_score,
                feasibility_score=feasibility_score,
                score=float(final_score),
                matched_skills=matched_skills,
            )
        )

    scored.sort(key=lambda item: item.score, reverse=True)
    top_projects = scored[: CONFIG.top_k]

    results: List[Dict] = []
    for idx, item in enumerate(top_projects):
        recommendation_type = "doable" if idx < 3 else "stretch"
        result = build_project_recommendation(
            project=item.project,
            user_input=user_input,
            matched_skills=item.matched_skills,
            recommendation_type=recommendation_type,
            score=item.score,
        )
        results.append(result)
    return results
