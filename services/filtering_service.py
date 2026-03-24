from __future__ import annotations

from typing import Dict, List

from services.preprocessing_service import ProcessedInput

DIFFICULTY_ORDER = {"easy": 1, "beginner": 1, "medium": 2, "intermediate": 2, "hard": 3, "advanced": 3}
TIME_COMPLEXITY_ORDER = {"short": 1, "medium": 2, "long": 3, "small": 1, "moderate": 2, "complex": 3, "high": 3}


def apply_feasibility_filters(projects: List[Dict], user_input: ProcessedInput) -> List[Dict]:
    """
    Remove clearly infeasible projects before ranking.
    """
    if not projects:
        return []

    user_exp = (user_input.experience_level or "intermediate").lower()
    user_time = (user_input.time_available or "medium").lower()
    exp_idx = DIFFICULTY_ORDER.get(user_exp, 2)
    time_idx = TIME_COMPLEXITY_ORDER.get(user_time, 2)

    filtered: List[Dict] = []
    for project in projects:
        difficulty = DIFFICULTY_ORDER.get(str(project.get("difficulty", "intermediate")).lower(), 2)
        complexity = TIME_COMPLEXITY_ORDER.get(str(project.get("complexity", "medium")).lower(), 2)
        if (difficulty - exp_idx) >= 2 and (complexity - time_idx) >= 1:
            continue
        filtered.append(project)

    return filtered if filtered else projects
