from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import sys

# Allow running as a script from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.enrich_projects import _embedding_text, _idea_block, _infer_archetype_text, _infer_domain_list  # noqa: E402
from core.model_loader import get_embedding_model  # noqa: E402


def _mk(
    *,
    title: str,
    description: str,
    dataset_link: str,
    domain: List[str],
    skills: List[str],
    difficulty: str = "medium",
) -> Dict[str, Any]:
    return {
        "title": title,
        "dataset_name": title,
        "description": description,
        "summary": description,
        "full_text": description,
        "dataset_link": dataset_link,
        "domain": domain,
        "skills": skills,
        "difficulty": difficulty,
    }


def curated() -> List[Dict[str, Any]]:
    # Verified links from web search results
    return [
        _mk(
            title="Missing People (CV Matching + Alerts)",
            description="Identify missing individuals by matching face embeddings from public reports and incoming photos; provide human-in-the-loop review and alert workflows.",
            dataset_link="https://www.kaggle.com/datasets/arjoonn/missing-people",
            domain=["Artificial Intelligence", "Computer Vision"],
            skills=["computer vision", "face recognition", "deep learning", "mlops", "deployment"],
            difficulty="hard",
        ),
        _mk(
            title="National Parks Missing Persons Risk Triage",
            description="Build a triage system to prioritize missing-person cases using spatiotemporal signals, resource constraints, and explainable risk scoring.",
            dataset_link="https://www.kaggle.com/datasets/thesagentist/open-missing-person-cases-inside-national-parks/data",
            domain=["Data Science", "Artificial Intelligence"],
            skills=["feature engineering", "forecasting", "explainability", "dashboards"],
            difficulty="medium",
        ),
        _mk(
            title="Chicago Crime Hotspot Forecasting Dashboard",
            description="Forecast incident hotspots by time and location; deliver a policy dashboard with confidence bands and ethical guardrails.",
            dataset_link="https://www.kaggle.com/datasets/redlineracer/chicago-crime-2015-2020",
            domain=["Data Science", "Artificial Intelligence"],
            skills=["time series", "geospatial", "forecasting", "dashboards", "evaluation"],
            difficulty="medium",
        ),
        _mk(
            title="San Francisco Crime Classification + Patrol Routing Insights",
            description="Predict crime categories from time and location and generate routing and patrol allocation insights with explainability.",
            dataset_link="https://www.kaggle.com/c/sf-crime/data",
            domain=["Machine Learning", "Artificial Intelligence"],
            skills=["classification", "calibration", "explainability", "feature engineering"],
            difficulty="medium",
        ),
        _mk(
            title="CrimeCast: Forecasting Crime Categories",
            description="Build a forecasting system that predicts the distribution of crime categories for upcoming periods; include monitoring and drift detection.",
            dataset_link="https://www.kaggle.com/competitions/crime-cast-forecasting-crime-categories/data",
            domain=["Data Science", "Artificial Intelligence"],
            skills=["forecasting", "time series", "mlops", "monitoring"],
            difficulty="hard",
        ),
        _mk(
            title="Women Harassment NLP Detector + Reporting Workflow",
            description="Detect harassment categories from reports/text and support a privacy-aware reporting workflow with evidence and escalation.",
            dataset_link="https://www.kaggle.com/datasets/thevincida/women-harassment-dataset",
            domain=["NLP", "Artificial Intelligence"],
            skills=["nlp", "text classification", "privacy", "deployment"],
            difficulty="medium",
        ),
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="embedded_projects_enriched.json")
    args = ap.parse_args()

    path = Path(args.file)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit("File must contain a list")

    model = get_embedding_model()

    existing_links = {str(p.get("dataset_link", "")).strip() for p in data if isinstance(p, dict)}
    add = []
    for p in curated():
        if p["dataset_link"] in existing_links:
            continue
        q = dict(p)
        q["domain"] = _infer_domain_list(q)
        q["project_idea"] = _idea_block(q)
        q["archetype_hint"] = _infer_archetype_text(q)
        emb = model.encode([_embedding_text(q)], convert_to_numpy=True, normalize_embeddings=False)[0]
        q["embedding"] = emb.tolist()
        add.append(q)

    if add:
        data.extend(add)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Appended {len(add)} curated projects to {path}")
    else:
        print("No curated projects added (already present).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

