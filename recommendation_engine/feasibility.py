"""Constraint-aware feasibility from time, difficulty, experience, and hardware."""

from __future__ import annotations

from typing import Dict, List, Tuple

from services.preprocessing_service import ProcessedInput

from recommendation_engine.domains import infer_ontology_domain, ontology_to_cluster

DIFFICULTY_ORDER = {"easy": 1, "beginner": 1, "medium": 2, "intermediate": 2, "hard": 3, "advanced": 3}
TIME_ORDER = {"short": 1, "medium": 2, "long": 3, "small": 1, "moderate": 2, "complex": 3, "high": 3}
COMPLEXITY_ORDER = {"short": 1, "medium": 2, "long": 3, "small": 1, "moderate": 2, "complex": 3, "high": 3}


def _hardware_is_limited(hw: str) -> bool:
    h = (hw or "").lower()
    return any(x in h for x in ("none", "limited", "minimal", "cpu only", "no gpu", "without gpu"))


def compute_feasibility(user: ProcessedInput, project: Dict) -> Tuple[float, List[str]]:
    notes: List[str] = []
    score = 1.0

    user_exp = (user.experience_level or "intermediate").lower()
    user_time = (user.time_available or "medium").lower()
    exp_idx = DIFFICULTY_ORDER.get(user_exp, 2)
    time_idx = TIME_ORDER.get(user_time, 2)

    proj_diff = DIFFICULTY_ORDER.get(str(project.get("difficulty", "intermediate")).lower(), 2)
    proj_complex = COMPLEXITY_ORDER.get(str(project.get("complexity", "medium")).lower(), 2)

    if proj_diff - exp_idx >= 2:
        score -= 0.35
        notes.append("Project difficulty is above your stated experience; scope may need trimming.")
    elif proj_diff > exp_idx:
        score -= 0.15
        notes.append("Slightly above your experience band—plan extra mentor review.")

    if proj_complex - time_idx >= 2:
        score -= 0.3
        notes.append("Complexity may exceed your available timeline unless you narrow deliverables.")
    elif proj_complex > time_idx:
        score -= 0.12
        notes.append("Timeline is tight versus complexity; prioritize a thin vertical slice.")

    if _hardware_is_limited(user.hardware_availability):
        cluster = ontology_to_cluster(infer_ontology_domain(project, user))
        if cluster in {"vision", "nlp"}:
            score -= 0.18
            notes.append("Heavy modeling stack—consider smaller models or cloud notebooks given hardware limits.")

    return float(max(0.0, min(1.0, score))), notes
