from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List

from core.config import CONFIG


_WHITESPACE_RE = re.compile(r"\s+")


@dataclass
class ProcessedInput:
    skills: List[str]
    interests: str
    experience_level: str
    time_available: str
    domain_preference: List[str]
    sector_context: str
    project_complexity_preference: str
    team_or_individual: str
    hardware_availability: str
    preferred_project_type: str
    dataset_comfort: str
    learning_vs_execution: str
    stretch_willingness: str
    semantic_query: str


def _normalize_text(value: str) -> str:
    cleaned = _WHITESPACE_RE.sub(" ", value.strip().lower())
    return cleaned


def _dedupe_preserve_order(values: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result


def process_user_input(payload: Dict[str, Any]) -> ProcessedInput:
    skills_raw = payload.get("skills", [])
    interests_raw = payload.get("interests", "")
    core_skills_raw = payload.get("core_skills", [])
    other_skills_raw = payload.get("other_skills", [])
    experience_raw = payload.get("experience_level", "")
    skill_confidence_raw = payload.get("skill_confidence_level", "")
    time_raw = payload.get("time_available", "")
    domains_raw = payload.get("domain_preference", [])
    complexity_pref_raw = payload.get("project_complexity_preference", "")
    team_raw = payload.get("team_or_individual", "")
    hardware_raw = payload.get("hardware_availability", "")
    project_type_raw = payload.get("preferred_project_type", "")
    dataset_comfort_raw = payload.get("dataset_comfort", "")
    learning_vs_execution_raw = payload.get("learning_vs_execution", "")
    stretch_raw = payload.get("stretch_willingness", "")
    sector_pick_raw = str(payload.get("sector_of_interest", "")).strip()
    sector_other_raw = str(payload.get("sector_of_interest_other", "")).strip()

    if not isinstance(skills_raw, list):
        raise ValueError("skills must be a list")
    if not isinstance(core_skills_raw, list):
        raise ValueError("core_skills must be a list")
    if not isinstance(other_skills_raw, list):
        raise ValueError("other_skills must be a list")
    if not isinstance(domains_raw, list):
        raise ValueError("domain_preference must be a list")

    combined_skills_raw = list(skills_raw) + list(core_skills_raw) + list(other_skills_raw)
    normalized_skills = _dedupe_preserve_order([skill for skill in (_normalize_text(str(s)) for s in combined_skills_raw) if skill])
    normalized_domains_input = _dedupe_preserve_order(
        [domain for domain in (_normalize_text(str(d)) for d in domains_raw) if domain]
    )

    supported_domain_map = {d.lower(): d for d in CONFIG.supported_domains}
    normalized_domains = [supported_domain_map[d] for d in normalized_domains_input if d in supported_domain_map]

    interests = _normalize_text(str(interests_raw))
    skill_confidence = _normalize_text(str(skill_confidence_raw))
    experience_level = _normalize_text(str(experience_raw)) or skill_confidence
    time_available = _normalize_text(str(time_raw))
    project_complexity_preference = _normalize_text(str(complexity_pref_raw))
    team_or_individual = _normalize_text(str(team_raw))
    hardware_availability = _normalize_text(str(hardware_raw))
    preferred_project_type = _normalize_text(str(project_type_raw))
    dataset_comfort = _normalize_text(str(dataset_comfort_raw))
    learning_vs_execution = _normalize_text(str(learning_vs_execution_raw))
    stretch_willingness = _normalize_text(str(stretch_raw))

    if sector_pick_raw.lower() == "other":
        sector_context = _normalize_text(sector_other_raw)
    else:
        sector_context = _normalize_text(sector_pick_raw)

    if experience_level and experience_level not in CONFIG.experience_levels:
        raise ValueError(f"experience_level must be one of: {', '.join(CONFIG.experience_levels)}")
    if time_available and time_available not in CONFIG.time_availability:
        raise ValueError(f"time_available must be one of: {', '.join(CONFIG.time_availability)}")

    semantic_parts: List[str] = []
    semantic_parts.extend(normalized_skills)
    if interests:
        semantic_parts.append(interests)
    if sector_context:
        semantic_parts.append(sector_context)
    semantic_parts.extend([d.lower() for d in normalized_domains])
    semantic_parts.extend(
        [
            project_complexity_preference,
            team_or_individual,
            hardware_availability,
            preferred_project_type,
            dataset_comfort,
            learning_vs_execution,
            stretch_willingness,
        ]
    )
    semantic_query = _normalize_text(" ".join(semantic_parts))

    return ProcessedInput(
        skills=normalized_skills,
        interests=interests,
        experience_level=experience_level,
        time_available=time_available,
        domain_preference=normalized_domains,
        sector_context=sector_context,
        project_complexity_preference=project_complexity_preference,
        team_or_individual=team_or_individual,
        hardware_availability=hardware_availability,
        preferred_project_type=preferred_project_type,
        dataset_comfort=dataset_comfort,
        learning_vs_execution=learning_vs_execution,
        stretch_willingness=stretch_willingness,
        semantic_query=semantic_query,
    )
