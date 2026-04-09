from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from core.config import CONFIG
from core.model_loader import get_embedding_model


class DataService:
    """Abstraction layer for project storage (JSON now, DB later)."""

    def __init__(self, embeddings_path: Path | None = None) -> None:
        self.embeddings_path = embeddings_path or CONFIG.embeddings_path

    @lru_cache(maxsize=1)
    def load_projects(self) -> List[Dict[str, Any]]:
        if not self.embeddings_path.exists():
            raise FileNotFoundError(f"Project data file not found: {self.embeddings_path}")

        with self.embeddings_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("embedded_projects.json must contain a list of projects")
        return data

    @lru_cache(maxsize=1)
    def get_projects_with_embeddings(self) -> tuple[List[Dict[str, Any]], np.ndarray]:
        projects = self.load_projects()
        vectors: List[np.ndarray] = []
        valid_projects: List[Dict[str, Any]] = []
        to_encode_indices: List[int] = []

        for idx, project in enumerate(projects):
            emb = project.get("embedding")
            if isinstance(emb, list) and emb:
                vectors.append(np.array(emb, dtype=np.float32))
            else:
                to_encode_indices.append(idx)
                vectors.append(np.zeros((384,), dtype=np.float32))

        if to_encode_indices:
            model = get_embedding_model()
            texts = [self._project_text(projects[idx]) for idx in to_encode_indices]
            encoded = model.encode(texts, convert_to_numpy=True, normalize_embeddings=False).astype(np.float32)
            for encoded_idx, project_idx in enumerate(to_encode_indices):
                vectors[project_idx] = encoded[encoded_idx]

        for project in projects:
            valid_projects.append(project)

        if not vectors:
            return [], np.empty((0, 0), dtype=np.float32)

        return valid_projects, np.vstack(vectors)

    @staticmethod
    def _project_text(project: Dict[str, Any]) -> str:
        title = str(project.get("title", ""))
        description = str(project.get("description", ""))
        summary = str(project.get("summary", ""))
        full_text = str(project.get("full_text", ""))
        idea = project.get("project_idea") or {}
        idea_fields = []
        if isinstance(idea, dict):
            idea_fields.extend(
                [
                    str(idea.get("use_case", "")),
                    str(idea.get("industry_context", "")),
                    str(idea.get("deliverables", "")),
                    str(idea.get("evaluation_plan", "")),
                    str(idea.get("deployment_plan", "")),
                ]
            )
        domains = " ".join(project.get("domain", []) if isinstance(project.get("domain"), list) else [project.get("domain", "")])
        skills = " ".join(project.get("skills", []))
        return " ".join([title, description, summary, full_text, " ".join(idea_fields), domains, skills]).strip()
