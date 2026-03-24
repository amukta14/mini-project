from __future__ import annotations

from typing import Dict, List

from services.preprocessing_service import ProcessedInput


def build_recommendation_reason(
    project: Dict,
    user_input: ProcessedInput,
    matched_skills: List[str],
    score_breakdown: Dict[str, float],
) -> str:
    domain = project.get("domain", [])
    if isinstance(domain, str):
        domain = [domain]

    reason_parts: List[str] = []
    if user_input.interests:
        reason_parts.append(f"is semantically aligned with your interest area ({user_input.interests})")
    if matched_skills:
        reason_parts.append(f"leverages your {', '.join(matched_skills)} skills")
    elif user_input.skills:
        reason_parts.append("introduces skills adjacent to your current profile")

    suitability = (
        f"suitable for your {user_input.experience_level} level"
        if user_input.experience_level
        else "compatible with mixed experience levels"
    )
    time_fit = (
        f"feasible within your {user_input.time_available} time availability"
        if user_input.time_available
        else "adaptable to different timelines"
    )

    domain_text = f"in the {', '.join(domain)} domain"
    body = " and ".join(reason_parts) if reason_parts else "matches your profile"
    score_text = (
        f" Signal quality: semantic {score_breakdown.get('semantic', 0):.2f},"
        f" skill {score_breakdown.get('skills', 0):.2f}, feasibility {score_breakdown.get('feasibility', 0):.2f}."
    )
    return f"This project {body} {domain_text}. It is {suitability} and {time_fit}.{score_text}"
