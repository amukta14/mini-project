"""Transform catalog rows into final-year style project ideas (not dataset listings)."""

from __future__ import annotations

import re
from typing import Dict, List, Set, Tuple

from services.preprocessing_service import ProcessedInput

from recommendation_engine.dataset_links import resolve_dataset
from recommendation_engine.display import format_difficulty, format_domain_label
from recommendation_engine.domains import infer_ontology_domain, ontology_to_cluster
from recommendation_engine.ranker import ScoredProject

_BANNED = re.compile(r"\bai[- ]?based\b|\bartificial intelligence system\b", re.I)

# Map fine-grained ontology clusters to template families with rich step libraries.
_TEMPLATE_CLUSTER = {
    "policy_law": "finance",
    "creative_signal": "nlp",
    "people_analytics": "education",
    "stem": "health",
    "responsible_ai": "education",
    "built_world": "commerce",
    "agriculture": "environment",
    "general": "general",
}


def _variant_seed(project: Dict, rank_index: int) -> int:
    return sum(ord(c) for c in str(project.get("title", ""))) + rank_index * 31


def _sector_phrase(project: Dict) -> str:
    s = str(project.get("sector") or "").strip()
    if s:
        return s
    return str(project.get("title", "this problem context")).split(":")[0].strip() or "the target sector"


def _clean_idea_sentence(project: Dict) -> str:
    idea = project.get("project_idea")
    if isinstance(idea, dict):
        uc = str(idea.get("use_case", "")).strip()
        if uc and len(uc) > 40 and not uc.lower().startswith("build a decision-support"):
            return uc.rstrip(".") + "."
    desc = str(project.get("description", "")).strip()
    if desc and len(desc) > 50:
        return desc[0].upper() + desc[1:]
    return ""


# (problem template index, title stems)
_TITLE_SETS: Dict[str, Tuple[str, ...]] = {
    "health": (
        "Calibrated risk triage for {sector}",
        "Operational signal review for {sector}",
        "Cohort analytics prototype for {sector}",
        "Measurement-backed decision memo for {sector}",
    ),
    "finance": (
        "Exposure scoring workspace for {sector}",
        "Anomaly surveillance slice for {sector}",
        "Policy-grade monitoring for {sector}",
        "Counterparty signal review for {sector}",
    ),
    "nlp": (
        "Language routing lab for {sector}",
        "Evidence-linked text workflow for {sector}",
        "Operational language QA for {sector}",
        "Structured narrative extraction for {sector}",
    ),
    "vision": (
        "Visual inspection harness for {sector}",
        "Screening workflow prototype for {sector}",
        "Geometric feature study for {sector}",
        "Label-efficient vision pilot for {sector}",
    ),
    "iot_industrial": (
        "Telemetry forecasting desk for {sector}",
        "Signal health monitor for {sector}",
        "Edge-to-cloud analytics for {sector}",
        "Reliability analytics for {sector}",
    ),
    "security": (
        "Event prioritization console for {sector}",
        "Calibrated alert triage for {sector}",
        "Analyst traceability view for {sector}",
        "Purple-team evaluation harness for {sector}",
    ),
    "environment": (
        "Scenario planning board for {sector}",
        "Signal fusion dashboard for {sector}",
        "Impact monitoring slice for {sector}",
        "Forecast comparison lab for {sector}",
    ),
    "education": (
        "Learning analytics pilot for {sector}",
        "Early-support signals for {sector}",
        "Fairness-aware reporting for {sector}",
        "Intervention design study for {sector}",
    ),
    "commerce": (
        "Demand sensing prototype for {sector}",
        "Assortment diagnostics for {sector}",
        "Customer journey forensics for {sector}",
        "Fulfillment risk desk for {sector}",
    ),
    "general": (
        "Decision memo prototype for {sector}",
        "Metric-driven review for {sector}",
        "Field validation study for {sector}",
        "Stakeholder-facing analytics for {sector}",
    ),
}


def _steps_for_cluster(cluster: str, dataset_name: str, variant: int) -> List[str]:
    cluster = _TEMPLATE_CLUSTER.get(cluster, cluster)
    ds = dataset_name
    # Four-step structure: data → model → eval → deploy (wording rotates)
    libraries: Dict[str, List[Tuple[str, str, str, str]]] = {
        "health": [
            (
                f"Frame outcomes and leakage rules using '{ds}'; document cohort exclusions and missingness.",
                "Fit a sparse logistic regression baseline with isotonic calibration for interpretable thresholds.",
                "Add a Random Forest with SHAP-style drivers; compare PR-AUC vs calibrated logistic on holdout patients.",
                "Ship a small FastAPI + static review UI with audit logging and a retraining checklist.",
            ),
            (
                f"Profile '{ds}' for label integrity; define clinically plausible feature groups.",
                "Prototype gradient-boosted trees with monotonic constraints on key vitals.",
                "Evaluate with sensitivity-focused metrics; stress-test subgroup slices.",
                "Deliver a reproducible notebook pipeline plus a deployment note for hospital IT constraints.",
            ),
        ],
        "finance": [
            (
                f"Normalize '{ds}' with time-aware splits; engineer transaction aggregates without peeking.",
                "Train XGBoost with scale_pos_weight tuned for rare fraud; track PR-AUC.",
                "Layer an isolation forest baseline; reconcile alerts with precision@k.",
                "Expose scores via FastAPI and a lightweight analyst console with drill-down to raw features.",
            ),
            (
                f"Define chargeback-aligned labels on '{ds}'; cap leakage from future timestamps.",
                "Calibrate tree ensembles; pick thresholds using explicit cost ratios.",
                "Run backtesting by month; document drift sentinels.",
                "Containerize scoring with environment pins and a monitoring runbook.",
            ),
        ],
        "nlp": [
            (
                f"Curate '{ds}' with deduping and language detection; freeze train/dev/test splits.",
                "Fine-tune a compact transformer head (e.g., DistilBERT) with class weights.",
                "Report macro-F1 and confusion by class; add error buckets for manual review.",
                "Deploy a batched inference service with caching and redaction hooks for PII.",
            ),
            (
                f"Tokenize '{ds}' with consistent preprocessing; store hashes for reproducibility.",
                "Compare linear baselines vs small transformers; early-stop on dev loss.",
                "Add token attributions for top errors; ship a reviewer queue.",
                "Publish a CLI + minimal web form for stakeholder demos.",
            ),
        ],
        "vision": [
            (
                f"Version image splits for '{ds}'; document augmentations and class priors.",
                "Train a CNN with transfer learning; track top-1 and calibration on a validation tail.",
                "Run Grad-CAM on failure buckets; capture qualitative review notes.",
                "Bundle a Gradio or Flask upload demo with latency notes for CPU vs GPU.",
            ),
        ],
        "iot_industrial": [
            (
                f"Resample '{ds}' to consistent windows; flag missing sensors and cold starts.",
                "Fit ARIMA/ETS baselines vs gradient boosting on lag features.",
                "Score with MAE and pinball loss; visualize residual seasonality.",
                "Expose forecasts through MQTT or REST with alert thresholds and backoff rules.",
            ),
            (
                f"Engineer rolling statistics on '{ds}'; align labels with maintenance events.",
                "Train tree models for failure classification; calibrate probabilities.",
                "Simulate alert policies to measure false alarm rates.",
                "Document edge deployment constraints and firmware update flow.",
            ),
        ],
        "security": [
            (
                f"Normalize '{ds}' to a common event schema; balance rare attack classes.",
                "Train one-class SVM / isolation forest plus XGBoost for hybrid scoring.",
                "Measure detection rate at fixed FPR; capture analyst time-to-triage.",
                "Ship a SOC-style triage board with evidence links and exportable cases.",
            ),
        ],
        "environment": [
            (
                f"Align '{ds}' to forecasting horizons; build leakage-safe temporal splits.",
                "Compare seasonal naive vs boosted regressors; quantify interval coverage.",
                "Stress-test heatwaves/outliers; publish scenario tables.",
                "Deliver a map-ready dashboard spec plus CSV exports for planners.",
            ),
        ],
        "education": [
            (
                f"Define fairness constraints for '{ds}'; anonymize identifiers rigorously.",
                "Train transparent models (logistic + shallow trees) with subgroup reports.",
                "Pair metrics with intervention simulations; avoid overclaiming causality.",
                "Provide an advisor-facing summary PDF + CSV of risk drivers.",
            ),
        ],
        "commerce": [
            (
                f"Engineer behavioral features from '{ds}'; validate leakage from future clicks.",
                "Train matrix factorization vs gradient boosting for propensity.",
                "Evaluate ranking metrics (nDCG@k) on held-out users.",
                "Expose recommendations behind a feature-flagged API with offline evaluation hooks.",
            ),
        ],
        "general": [
            (
                f"Profile '{ds}' with schema contracts and data-quality tests.",
                "Train elastic-net and gradient-boosted baselines with cross-validation.",
                "Report calibration and error analysis by segment.",
                "Ship a FastAPI service plus README with reproduction steps.",
            ),
            (
                f"Define KPIs tied to '{ds}' and document assumptions.",
                "Compare linear models vs tree ensembles; pick with ablation notes.",
                "Add statistical sanity checks and bootstrap intervals.",
                "Publish a stakeholder brief with limitations and next experiments.",
            ),
        ],
    }
    pool = libraries.get(cluster) or libraries["general"]
    choice = pool[variant % len(pool)]
    return list(choice)


def _tech_stack(cluster: str, variant: int, matched: List[str], user: ProcessedInput) -> List[str]:
    cluster = _TEMPLATE_CLUSTER.get(cluster, cluster)
    base: Dict[str, List[str]] = {
        "health": ["Python", "scikit-learn", "pandas", "FastAPI", "SHAP"],
        "finance": ["Python", "XGBoost", "pandas", "FastAPI", "matplotlib"],
        "nlp": ["Python", "PyTorch", "transformers", "datasets", "FastAPI"],
        "vision": ["Python", "PyTorch", "torchvision", "OpenCV", "Gradio"],
        "iot_industrial": ["Python", "pandas", "scikit-learn", "MQTT", "Docker"],
        "security": ["Python", "scikit-learn", "pandas", "FastAPI", "Elasticsearch"],
        "environment": ["Python", "pandas", "scikit-learn", "Plotly", "FastAPI"],
        "education": ["Python", "pandas", "scikit-learn", "Fairlearn", "Jupyter"],
        "commerce": ["Python", "pandas", "scikit-learn", "implicit", "FastAPI"],
        "general": ["Python", "pandas", "scikit-learn", "FastAPI", "pytest", "pydantic"],
    }
    stack = list(base.get(cluster, base["general"]))
    for m in matched[:2]:
        t = m.strip().title()
        if t and t not in stack:
            stack.insert(0, t)
    if user.preferred_project_type == "research":
        if "Jupyter" not in stack:
            stack.append("Jupyter")
    if variant % 2 == 0 and "Docker" not in stack:
        stack.append("Docker")
    dedup: List[str] = []
    for x in stack:
        if x not in dedup:
            dedup.append(x)
    return dedup[:8]


def build_title(cluster: str, project: Dict, variant: int) -> str:
    cluster = _TEMPLATE_CLUSTER.get(cluster, cluster)
    sector = _sector_phrase(project)
    stems = _TITLE_SETS.get(cluster, _TITLE_SETS["general"])
    stem = stems[variant % len(stems)].format(sector=sector)
    if _BANNED.search(stem):
        stem = _TITLE_SETS["general"][variant % len(_TITLE_SETS["general"])].format(sector=sector)
    return stem


def build_problem_statement(ontology_domain: str, project: Dict, user: ProcessedInput) -> str:
    custom = _clean_idea_sentence(project)
    if custom and len(custom) > 60:
        return custom
    sector = _sector_phrase(project)
    interest = user.interests or "your capstone goals"
    return (
        f"Deliver measurable insight for {format_domain_label(ontology_domain)} stakeholders in {sector}, "
        f"grounded in accountable modeling and aligned with {interest}."
    )


def build_project_description(
    ontology_domain: str, project: Dict, user: ProcessedInput, dataset_name: str
) -> str:
    sector = _sector_phrase(project)
    focus = user.preferred_project_type or "implementation"
    return (
        f"This capstone frames a {format_domain_label(ontology_domain)} problem in {sector}: "
        f"you will treat '{dataset_name}' as the initial evidence base, iterate models with disciplined evaluation, "
        f"and present a {focus}-ready artifact reviewers can run end-to-end."
    )


def build_reason(sp: ScoredProject, user: ProcessedInput, ontology_domain: str) -> str:
    skills_txt = ", ".join(sp.matched_skills[:4]) if sp.matched_skills else "foundational tooling"
    fe = "; ".join(sp.feasibility_notes[:2]) if sp.feasibility_notes else "no major feasibility flags"
    return (
        f"Semantic fit is strong for {format_domain_label(ontology_domain)} work matching your interests; "
        f"skills ({skills_txt}) cover key needs; feasibility notes: {fe}. "
        f"Weighted blend uses 60% semantics, 25% skill overlap, 15% feasibility."
    )


def generate_recommendation(
    sp: ScoredProject,
    user: ProcessedInput,
    rank_index: int,
    used_titles: Set[str],
) -> Dict:
    ontology = infer_ontology_domain(sp.project, user)
    cluster = ontology_to_cluster(ontology)
    variant = _variant_seed(sp.project, rank_index)

    dataset_name, dataset_link = resolve_dataset(sp.project, cluster)

    title = build_title(cluster, sp.project, variant)
    if title in used_titles:
        title = f"{title} — design variant {variant % 7 + 1}"
    used_titles.add(title)

    rec_type = "doable" if rank_index < 3 else "stretch"

    return {
        "title": title,
        "domain": format_domain_label(ontology),
        "problem_statement": build_problem_statement(ontology, sp.project, user),
        "project_description": build_project_description(ontology, sp.project, user, dataset_name),
        "implementation_approach": _steps_for_cluster(cluster, dataset_name, variant),
        "tech_stack": _tech_stack(cluster, variant, sp.matched_skills, user),
        "dataset": {"name": dataset_name, "link": dataset_link},
        "difficulty": format_difficulty(sp.project),
        "score": round(sp.final_score, 4),
        "type": rec_type,
        "reason": build_reason(sp, user, ontology),
    }
