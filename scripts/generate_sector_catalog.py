from __future__ import annotations

import argparse
import json
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import numpy as np


_WS = re.compile(r"\s+")


def _clean(s: str) -> str:
    return _WS.sub(" ", (s or "").strip())


def _slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s or "sector"


@dataclass(frozen=True)
class IdeaTemplate:
    name: str
    archetype: str
    domain: List[str]
    skills: List[str]
    difficulty: str
    dataset_queries: List[str]


TEMPLATES: List[IdeaTemplate] = [
    IdeaTemplate(
        name="Decision-support dashboard",
        archetype="generic_predictive",
        domain=["Data Science", "Artificial Intelligence"],
        skills=["feature engineering", "explainability", "dashboards", "evaluation"],
        difficulty="medium",
        dataset_queries=["{sector} incidents dataset", "{sector} operational logs dataset", "{sector} metrics time series dataset"],
    ),
    IdeaTemplate(
        name="Forecasting + scenarios",
        archetype="time_series_forecasting",
        domain=["Data Science", "Artificial Intelligence"],
        skills=["time series", "forecasting", "monitoring", "deployment"],
        difficulty="hard",
        dataset_queries=["{sector} demand forecasting dataset", "{sector} time series dataset", "{sector} seasonality dataset"],
    ),
    IdeaTemplate(
        name="NLP complaints & reports triage",
        archetype="nlp_text_classification",
        domain=["NLP", "Artificial Intelligence"],
        skills=["nlp", "text classification", "privacy", "deployment"],
        difficulty="medium",
        dataset_queries=["{sector} complaint dataset", "{sector} incident reports dataset", "{sector} feedback text dataset"],
    ),
    IdeaTemplate(
        name="Computer vision safety monitor",
        archetype="cv_medical_screening",
        domain=["Computer Vision", "Artificial Intelligence"],
        skills=["computer vision", "deep learning", "evaluation", "explainability"],
        difficulty="hard",
        dataset_queries=["{sector} cctv dataset", "{sector} surveillance dataset", "{sector} object detection dataset"],
    ),
    IdeaTemplate(
        name="Fraud/anomaly detection pipeline",
        archetype="fraud_anomaly",
        domain=["Machine Learning", "Artificial Intelligence"],
        skills=["anomaly detection", "calibration", "mlops", "monitoring"],
        difficulty="hard",
        dataset_queries=["{sector} fraud dataset", "{sector} transaction dataset", "{sector} anomalies dataset"],
    ),
]


CURATED_DATASET_LINKS: Dict[str, List[Dict[str, str]]] = {
    # A small curated set; most ideas will rely on dataset queries.
    "agriculture": [
        {
            "name": "Crop Disease Image Classification Dataset",
            "link": "https://www.kaggle.com/datasets/killa92/crop-disease-image-classification-dataset",
        },
        {
            "name": "Global dataset of yields of major crops (1981-2016)",
            "link": "https://www.kaggle.com/datasets/mukherjeedebrup/global-dataset-of-yields-of-major-crops1981-2016",
        },
        {
            "name": "Crop Yield Prediction Dataset",
            "link": "https://www.kaggle.com/datasets/patelris/crop-yield-prediction-dataset",
        },
    ],
    "justice-public-safety": [
        {"name": "Chicago Crime (2015 - 2020)", "link": "https://www.kaggle.com/datasets/redlineracer/chicago-crime-2015-2020"},
        {"name": "San Francisco Crime Classification", "link": "https://www.kaggle.com/c/sf-crime/data"},
    ],
    "women-safety": [
        {"name": "Women harassment dataset", "link": "https://www.kaggle.com/datasets/thevincida/women-harassment-dataset"}
    ],
    "environmental-monitoring": [
        {"name": "Wildfire Satellite Data", "link": "https://www.kaggle.com/datasets/washingtongold/wildfire-satellite-data"},
        {"name": "Wildfire Detection Image Data", "link": "https://www.kaggle.com/datasets/brsdincer/wildfire-detection-image-data"},
    ],
    "edtech": [
        {
            "name": "Student Performance UCI Dataset",
            "link": "https://www.kaggle.com/datasets/abhirupadhikary/student-performance-uci-dataset",
        },
        {
            "name": "Predict Student Performance Dataset",
            "link": "https://www.kaggle.com/datasets/stealthtechnologies/predict-student-performance-dataset",
        },
    ],
    "fashion": [
        {
            "name": "Fashion Product Images Dataset",
            "link": "https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset",
        }
    ],
    "cybersecurity": [
        {
            "name": "NSL-KDD Intrusion Detection Dataset",
            "link": "https://www.kaggle.com/datasets/programmer3/nsl-kdd-intrusion-detection-dataset",
        },
        {
            "name": "Intrusion Detection (CICIDS2017)",
            "link": "https://www.kaggle.com/datasets/elshewey/intrusion-detection-cicids2017",
        },
        {
            "name": "Network Intrusion Detection Dataset (UNR-IDD)",
            "link": "https://www.kaggle.com/datasets/mostafanofal/network-intrusion-detection-dataset-unr-idd",
        },
    ],
    "supply-chain": [
        {"name": "Supply Chain Dataset", "link": "https://www.kaggle.com/datasets/programmer3/supply-chain-dataset"},
        {
            "name": "Porter Delivery Time Estimation Dataset",
            "link": "https://www.kaggle.com/datasets/ranitsarkar01/porter-delivery-time-estimation-dataset",
        },
    ],
}

SECTOR_THEMES: Dict[str, Dict[str, List[str]]] = {
    "justice-public-safety": {
        "stakeholders": [
            "public safety analysts",
            "city operations teams",
            "community safety programs",
            "emergency dispatch coordinators",
        ],
        "problems": [
            "prioritize patrol routes with measurable impact",
            "identify emerging hotspots without over-policing bias",
            "reduce response times for high-severity incidents",
            "build transparency dashboards for community oversight",
        ],
    },
    "women-safety": {
        "stakeholders": ["safety NGOs", "campus security teams", "city helplines", "community moderators"],
        "problems": [
            "triage harassment reports quickly and safely",
            "detect unsafe zones and time windows to trigger alerts",
            "support anonymous reporting with evidence trails",
            "reduce false alarms with calibrated risk scoring",
        ],
    },
    "edtech": {
        "stakeholders": ["academic advisors", "course instructors", "student success teams", "training coordinators"],
        "problems": [
            "predict dropout risk early and recommend interventions",
            "personalize learning paths based on gaps and goals",
            "identify assessment bias and fairness issues",
            "forecast course demand and optimize scheduling",
        ],
    },
}


def build_idea(
    *,
    sector: str,
    sector_slug: str,
    idx: int,
    rng: random.Random,
    template: IdeaTemplate,
    curated: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    theme = SECTOR_THEMES.get(sector_slug, {})
    problem = rng.choice(
        theme.get(
            "problems",
            [
                "reduce risk and improve response time",
                "optimize resource allocation under constraints",
                "increase transparency and auditability of decisions",
                "detect early warning signals before escalation",
                "support stakeholders with explainable recommendations",
            ],
        )
    )
    stakeholder = rng.choice(
        theme.get(
            "stakeholders",
            [
                "operations teams",
                "policy makers",
                "risk analysts",
                "field coordinators",
                "frontline staff",
                "citizen support teams",
            ],
        )
    )
    deliverables = [
        "Production-grade data pipeline with validation checks",
        "Model + evaluation report with segment error analysis",
        "Interactive demo (dashboard/API) with role-based views",
    ]
    if template.archetype == "time_series_forecasting":
        deliverables = [
            "Forecast model suite + baselines with backtesting",
            "Scenario simulator with confidence bands",
            "Monitoring plan (drift + retraining cadence)",
        ]
    elif template.archetype == "nlp_text_classification":
        deliverables = [
            "Text triage model + explanation snippets",
            "Evidence panel linking predictions to source text",
            "Privacy-aware storage and redaction policy",
        ]
    elif template.archetype == "fraud_anomaly":
        deliverables = [
            "Risk scoring service with calibrated probabilities",
            "Case triage UI (top risky events + reasons)",
            "Monitoring and retraining triggers documentation",
        ]
    elif template.archetype == "cv_medical_screening":
        deliverables = [
            "Vision model baseline + transfer learning",
            "Explainability artifacts (heatmaps/failure gallery)",
            "Demo workflow: upload → prediction → evidence",
        ]

    title = f"{sector}: {template.name} ({idx + 1})"
    use_case = f"Build a {template.name.lower()} for {sector} to {problem} for {stakeholder}."

    # Provide multiple dataset options when curated links exist, to avoid repeating the same dataset everywhere.
    curated_pool = CURATED_DATASET_LINKS.get(sector_slug, [])
    dataset_options = curated_pool[:] if curated_pool else ([curated] if curated else [])
    rng.shuffle(dataset_options)
    dataset_options = dataset_options[: min(3, len(dataset_options))]
    chosen = dataset_options[0] if dataset_options else None

    dataset_link = str(chosen["link"]).strip() if chosen else ""
    dataset_name = str(chosen["name"]).strip() if chosen else ""
    dq = [q.format(sector=sector) for q in template.dataset_queries]

    if not dataset_link and dq:
        dataset_name = dq[0]
        dataset_link = f"https://www.kaggle.com/search?q={quote_plus(dq[0])}"
    if not dataset_name:
        dataset_name = dq[0] if dq else f"{sector} open dataset"
    if not dataset_link:
        dataset_link = f"https://www.kaggle.com/search?q={quote_plus(dataset_name)}"

    return {
        "title": title,
        "dataset_name": dataset_name,
        "dataset_link": dataset_link,
        "dataset_options": dataset_options,
        "dataset_queries": dq,
        "domain": template.domain,
        "skills": template.skills,
        "difficulty": template.difficulty,
        "archetype_hint": template.archetype,
        "description": _clean(use_case),
        "summary": _clean(use_case),
        "full_text": _clean(
            " ".join(
                [
                    use_case,
                    f"Sector: {sector}.",
                    f"Primary stakeholders: {stakeholder}.",
                    f"Deliverables: {', '.join(deliverables)}.",
                    "Evaluation: task-aligned metrics, calibration where needed, robustness and drift checks, and ablation/error analysis.",
                    "Deployment: reproducible pipeline, versioned artifacts, and a demo with monitoring hooks.",
                ]
            )
        ),
        "sector": sector,
        "sector_slug": sector_slug,
        "project_idea": {
            "use_case": _clean(use_case),
            "industry_context": _clean(
                f"In {sector}, teams need systems that are accurate, explainable, and operationally usable — not just models. "
                f"This project targets {stakeholder} with measurable outcomes and audit-friendly outputs."
            ),
            "deliverables": deliverables,
            "evaluation_plan": "Use task-aligned metrics, segment diagnostics, calibration (if classification), robustness checks, and drift monitoring signals.",
            "deployment_plan": "Ship a reproducible pipeline + a demo (API/dashboard). Add logging, monitoring, and a retraining cadence plan.",
        },
    }


def embed_text(p: Dict[str, Any]) -> str:
    idea = p.get("project_idea") or {}
    deliverables = ""
    if isinstance(idea, dict):
        d = idea.get("deliverables")
        if isinstance(d, list):
            deliverables = " ".join(str(x) for x in d)
    return _clean(
        " ".join(
            [
                str(p.get("title", "")),
                str(p.get("description", "")),
                str(p.get("summary", "")),
                str(p.get("full_text", "")),
                str(idea.get("use_case", "")) if isinstance(idea, dict) else "",
                str(idea.get("industry_context", "")) if isinstance(idea, dict) else "",
                deliverables,
                str(idea.get("evaluation_plan", "")) if isinstance(idea, dict) else "",
                str(idea.get("deployment_plan", "")) if isinstance(idea, dict) else "",
                " ".join(p.get("domain", []) if isinstance(p.get("domain"), list) else [str(p.get("domain", ""))]),
                " ".join(p.get("skills", []) if isinstance(p.get("skills"), list) else [str(p.get("skills", ""))]),
                " ".join(p.get("dataset_queries", []) if isinstance(p.get("dataset_queries"), list) else []),
            ]
        )
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sectors", default="data/sectors.json")
    ap.add_argument("--out", default="embedded_projects_mega.json")
    ap.add_argument("--per-sector", type=int, default=30)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--embed", action="store_true", help="Compute embeddings (slower, but best recommendations)")
    ap.add_argument("--batch", type=int, default=128)
    args = ap.parse_args()

    sectors_path = Path(args.sectors)
    out_path = Path(args.out)
    data = json.loads(sectors_path.read_text(encoding="utf-8"))
    sectors = data.get("sectors", [])
    if not isinstance(sectors, list) or not sectors:
        raise SystemExit("No sectors found")

    rng = random.Random(args.seed)
    ideas: List[Dict[str, Any]] = []

    for s in sectors:
        sector = _clean(str(s))
        slug = _slug(sector)
        curated = CURATED_DATASET_LINKS.get(slug, [])
        for i in range(args.per_sector):
            template = rng.choice(TEMPLATES)
            curated_pick = curated[i % len(curated)] if curated else None
            ideas.append(build_idea(sector=sector, sector_slug=slug, idx=i, rng=rng, template=template, curated=curated_pick))

    if args.embed:
        # Import only when needed to keep generation fast.
        import sys

        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from core.model_loader import get_embedding_model  # noqa: E402

        model = get_embedding_model()
        texts = [embed_text(p) for p in ideas]
        vectors: List[np.ndarray] = []
        for start in range(0, len(texts), args.batch):
            chunk = texts[start : start + args.batch]
            enc = model.encode(chunk, convert_to_numpy=True, normalize_embeddings=False).astype(np.float32)
            vectors.extend(list(enc))
        for i, v in enumerate(vectors):
            ideas[i]["embedding"] = v.tolist()

    out_path.write_text(json.dumps(ideas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(ideas)} projects to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

