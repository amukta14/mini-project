from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


BASE_DIR = Path(__file__).resolve().parent.parent


def _default_embeddings_path() -> Path:
    """Prefer small curated catalog when present; otherwise mega/enriched embedded JSON."""
    curated = BASE_DIR / "curated_projects.json"
    if curated.exists():
        return curated
    if (BASE_DIR / "embedded_projects_mega.json").exists():
        return BASE_DIR / "embedded_projects_mega.json"
    if (BASE_DIR / "embedded_projects_enriched.json").exists():
        return BASE_DIR / "embedded_projects_enriched.json"
    if (BASE_DIR / "embedded_projects.json").exists():
        return BASE_DIR / "embedded_projects.json"
    return BASE_DIR / "data" / "embedded_projects.json"


@dataclass(frozen=True)
class RankingWeights:
    semantic: float = 0.6
    skill: float = 0.25
    feasibility: float = 0.15

    def as_dict(self) -> Dict[str, float]:
        return {
            "semantic": self.semantic,
            "skill": self.skill,
            "feasibility": self.feasibility,
        }


@dataclass(frozen=True)
class AppConfig:
    model_name: str = "all-MiniLM-L6-v2"
    local_model_dir: Path = BASE_DIR / "models" / "all-MiniLM-L6-v2"
    embeddings_path: Path = field(default_factory=_default_embeddings_path)
    top_k: int = 12
    ranking_weights: RankingWeights = field(default_factory=RankingWeights)
    supported_domains: List[str] = field(
        default_factory=lambda: [
            "Artificial Intelligence",
            "Machine Learning",
            "Data Science",
            "Data Engineering",
            "Web Development",
            "Mobile Development",
            "Cloud Computing",
            "DevOps",
            "MLOps",
            "Cybersecurity",
            "IoT",
            "Embedded Systems",
            "NLP",
            "Computer Vision",
            "Blockchain",
            "Software Engineering",
            "Game Development",
            "UI/UX Design",
            "Robotics",
            "Education",
        ]
    )
    experience_levels: List[str] = field(default_factory=lambda: ["beginner", "intermediate", "advanced"])
    time_availability: List[str] = field(default_factory=lambda: ["short", "medium", "long"])


CONFIG = AppConfig()
