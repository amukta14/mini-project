from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


BASE_DIR = Path(__file__).resolve().parent.parent


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
    embeddings_path: Path = (
        BASE_DIR / "embedded_projects_mega.json"
        if (BASE_DIR / "embedded_projects_mega.json").exists()
        else (
            BASE_DIR / "embedded_projects_enriched.json"
            if (BASE_DIR / "embedded_projects_enriched.json").exists()
            else (
                BASE_DIR / "embedded_projects.json"
                if (BASE_DIR / "embedded_projects.json").exists()
                else BASE_DIR / "data" / "embedded_projects.json"
            )
        )
    )
    top_k: int = 5
    ranking_weights: RankingWeights = field(default_factory=RankingWeights)
    supported_domains: List[str] = field(
        default_factory=lambda: [
            "Artificial Intelligence",
            "Machine Learning",
            "Data Science",
            "Web Development",
            "Mobile Development",
            "IoT",
            "Cybersecurity",
            "Cloud Computing",
            "Blockchain",
            "NLP",
            "Computer Vision",
            "Education",
        ]
    )
    experience_levels: List[str] = field(default_factory=lambda: ["beginner", "intermediate", "advanced"])
    time_availability: List[str] = field(default_factory=lambda: ["short", "medium", "long"])


CONFIG = AppConfig()
