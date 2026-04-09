from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

import sys

# Allow running as a script from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.model_loader import get_embedding_model  # noqa: E402


_WS = re.compile(r"\s+")


def _clean(s: str) -> str:
    return _WS.sub(" ", (s or "").strip())


def _to_list(v: Any) -> List[str]:
    if isinstance(v, list):
        return [str(x) for x in v if str(x).strip()]
    if isinstance(v, str) and v.strip():
        return [v.strip()]
    return []


def _infer_domain_list(p: Dict[str, Any]) -> List[str]:
    d = p.get("domain")
    if isinstance(d, list):
        return [str(x) for x in d if str(x).strip()]
    if isinstance(d, str) and d.strip():
        return [d.strip()]
    return []


def _infer_archetype_text(p: Dict[str, Any]) -> str:
    t = " ".join(
        [
            str(p.get("title", "")),
            str(p.get("description", "")),
            str(p.get("summary", "")),
            str(p.get("full_text", "")),
            " ".join(_infer_domain_list(p)),
            " ".join(_to_list(p.get("skills"))),
        ]
    ).lower()
    for k, name in [
        ("fraud", "fraud_anomaly"),
        ("anomaly", "fraud_anomaly"),
        ("salary", "jobs_salary_analytics"),
        ("glassdoor", "jobs_salary_analytics"),
        ("hiring", "hr_hiring_analytics"),
        ("resume", "hr_hiring_analytics"),
        ("candidate", "hr_hiring_analytics"),
        ("crime", "crime_justice_analytics"),
        ("police", "crime_justice_analytics"),
        ("breast cancer", "cv_medical_screening"),
        ("mammogram", "cv_medical_screening"),
        ("x-ray", "cv_medical_screening"),
        ("xray", "cv_medical_screening"),
        ("diabetes", "health_risk_prediction"),
        ("stroke", "health_risk_prediction"),
        ("sepsis", "health_risk_prediction"),
        ("time series", "time_series_forecasting"),
        ("forecast", "time_series_forecasting"),
        ("nlp", "nlp_trend_summarization"),
        ("text", "nlp_trend_summarization"),
        ("news", "nlp_trend_summarization"),
        ("article", "nlp_trend_summarization"),
        ("review", "nlp_text_classification"),
        ("sentiment", "nlp_text_classification"),
    ]:
        if k in t:
            return name
    return "generic_predictive"


def _project_title(p: Dict[str, Any]) -> str:
    raw = _clean(str(p.get("title", "Project")))
    raw = re.sub(r"\bdataset\b", "", raw, flags=re.I).strip(" -:")
    if not raw:
        raw = "Project"
    return raw


def _idea_block(p: Dict[str, Any]) -> Dict[str, Any]:
    archetype = _infer_archetype_text(p)
    title = _project_title(p)
    domains = _infer_domain_list(p)
    primary_domain = (domains[0] if domains else "Applied AI").strip()

    if archetype == "fraud_anomaly":
        return {
            "use_case": f"Real-time fraud risk scoring and case triage for {title}.",
            "industry_context": "Fintech / payments risk teams need explainable, low-latency fraud detection with drift monitoring.",
            "deliverables": [
                "Fraud scoring API with calibrated probabilities",
                "Investigator console (top risky transactions + reasons)",
                "Drift & performance monitoring report",
            ],
            "evaluation_plan": "PR-AUC + cost-weighted thresholding, time-based validation, drift checks, investigator feedback loop.",
            "deployment_plan": "Batch training + versioned model registry, online scoring service, monitoring dashboards.",
        }
    if archetype == "jobs_salary_analytics":
        return {
            "use_case": f"Career intelligence platform using {title}: salary ranges, demand signals, and skill recommendations.",
            "industry_context": "Students and job seekers need transparent insights; models must report uncertainty and avoid misleading point estimates.",
            "deliverables": [
                "Salary range predictor with uncertainty intervals",
                "Skill-to-salary lift insights and role clustering",
                "Interactive dashboard for exploration and reports",
            ],
            "evaluation_plan": "MAE/RMSE for regression, interval coverage, segment analysis by role/location.",
            "deployment_plan": "Dashboard + API for predictions, scheduled data refresh, caching and observability.",
        }
    if archetype == "hr_hiring_analytics":
        return {
            "use_case": f"Candidate ranking assistant for {title} with auditability and fairness checks.",
            "industry_context": "Hiring systems require transparency, bias testing, and clear reasoning for every recommendation.",
            "deliverables": [
                "Ranking model + explanation panel",
                "Fairness & bias evaluation notebook",
                "Recruiter UI for shortlisting and feedback",
            ],
            "evaluation_plan": "Ranking metrics (NDCG/precision@k) + subgroup performance, bias probes, audit logs.",
            "deployment_plan": "Secure web app with role-based access, immutable logs, and periodic re-evaluation.",
        }
    if archetype == "crime_justice_analytics":
        return {
            "use_case": f"Public safety analytics tool for {title}: hotspot insights and risk-informed planning.",
            "industry_context": "Analytics must avoid misuse; outputs should be explainable and framed as decision support with guardrails.",
            "deliverables": [
                "Spatiotemporal hotspot maps + trend dashboard",
                "Time-based forecasting or risk scoring module",
                "Ethics + limitations report with misuse prevention",
            ],
            "evaluation_plan": "Time-based splits, calibration checks, segment diagnostics, and scenario analysis.",
            "deployment_plan": "Dashboard with access controls, reproducible pipelines, and documentation for stakeholders.",
        }
    if archetype == "cv_medical_screening":
        return {
            "use_case": f"Medical image triage prototype using {title} with explainable outputs for clinicians.",
            "industry_context": "Screening tasks prioritize sensitivity; models must show visual evidence and failure cases.",
            "deliverables": [
                "Vision model baseline + transfer learning",
                "Grad-CAM/heatmap explanation gallery",
                "Clinician-style demo: upload → prediction + evidence",
            ],
            "evaluation_plan": "Sensitivity-first operating points, ROC/AUC, subgroup/failure analysis, confidence calibration.",
            "deployment_plan": "Lightweight web demo, secure data handling assumptions, and clear non-clinical disclaimer.",
        }
    if archetype == "health_risk_prediction":
        return {
            "use_case": f"Patient risk stratification and intervention insights using {title}.",
            "industry_context": "Healthcare ML needs calibrated risk scores and interpretable drivers; evaluation must reflect clinical tradeoffs.",
            "deliverables": [
                "Calibrated risk model + threshold policy",
                "Patient-level explanations + cohort insights",
                "Decision-support dashboard or report",
            ],
            "evaluation_plan": "AUC/PR-AUC + calibration, threshold tradeoffs, error analysis by cohort.",
            "deployment_plan": "Batch scoring + API, monitoring, retraining cadence, and governance notes.",
        }
    if archetype == "time_series_forecasting":
        return {
            "use_case": f"Forecasting system for {title} with scenarios and confidence bands.",
            "industry_context": "Forecasts must quantify uncertainty and adapt to seasonality and drift.",
            "deliverables": [
                "Forecast model suite + baselines",
                "Intervals (prediction bands) + anomaly alerts",
                "Dashboard for scenarios and monitoring",
            ],
            "evaluation_plan": "MAE/MAPE + interval coverage, backtesting, seasonal diagnostics.",
            "deployment_plan": "Scheduled retraining, batch inference, and dashboard with confidence bands.",
        }
    if archetype in {"nlp_trend_summarization", "nlp_text_classification"}:
        return {
            "use_case": f"NLP insight explorer for {title}: themes, summaries, and evidence-backed insights.",
            "industry_context": "Stakeholders need traceability—every insight should link back to original sources.",
            "deliverables": [
                "Embedding-based clustering + topic explorer",
                "Summaries and evidence panels",
                "Search + timeline views for trend shifts",
            ],
            "evaluation_plan": "Human evaluation rubric + retrieval precision checks + qualitative failure cases.",
            "deployment_plan": "Interactive explorer with caching, indexing, and reproducible pipeline runs.",
        }

    return {
        "use_case": f"Industry-style {primary_domain} project using {title} as the underlying dataset.",
        "industry_context": "Focus on measurable impact, stakeholder needs, and a deployable demo with evaluation.",
        "deliverables": [
            "End-to-end data pipeline + model",
            "Evaluation + error analysis report",
            "Demo (API or dashboard) + documentation",
        ],
        "evaluation_plan": "Metrics aligned to the task, segment analysis, and robustness checks.",
        "deployment_plan": "Reproducible pipeline, versioned artifacts, and a lightweight demo deployment.",
    }


def _embedding_text(p: Dict[str, Any]) -> str:
    domains = " ".join(_infer_domain_list(p))
    skills = " ".join(_to_list(p.get("skills")))
    idea = p.get("project_idea") or {}
    deliverables = ""
    if isinstance(idea, dict):
        d = idea.get("deliverables")
        if isinstance(d, list):
            deliverables = " ".join(str(x) for x in d)
        else:
            deliverables = str(d or "")
    return _clean(
        " ".join(
            [
                str(p.get("title", "")),
                str(p.get("summary", "")),
                str(p.get("description", "")),
                str(p.get("full_text", "")),
                str(idea.get("use_case", "")) if isinstance(idea, dict) else "",
                str(idea.get("industry_context", "")) if isinstance(idea, dict) else "",
                deliverables,
                str(idea.get("evaluation_plan", "")) if isinstance(idea, dict) else "",
                str(idea.get("deployment_plan", "")) if isinstance(idea, dict) else "",
                domains,
                skills,
            ]
        )
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_path", default="embedded_projects.json")
    ap.add_argument("--out", dest="out_path", default="embedded_projects_enriched.json")
    ap.add_argument("--reembed", action="store_true", help="Recompute embeddings from enriched text")
    args = ap.parse_args()

    in_path = Path(args.in_path)
    out_path = Path(args.out_path)

    data = json.loads(in_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit("Input JSON must be a list of projects")

    enriched: List[Dict[str, Any]] = []
    texts: List[str] = []
    for p in data:
        if not isinstance(p, dict):
            continue
        q = dict(p)
        # Normalize domain to list
        q["domain"] = _infer_domain_list(q)
        # Generate richer project idea block
        q["project_idea"] = _idea_block(q)
        q["archetype_hint"] = _infer_archetype_text(q)
        texts.append(_embedding_text(q))
        enriched.append(q)

    if args.reembed:
        model = get_embedding_model()
        enc = model.encode(texts, convert_to_numpy=True, normalize_embeddings=False).astype(np.float32)
        for i, v in enumerate(enc):
            enriched[i]["embedding"] = v.tolist()

    out_path.write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(enriched)} projects to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

