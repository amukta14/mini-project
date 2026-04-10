from __future__ import annotations

import re
from typing import Dict, List, Literal, Tuple, cast
from urllib.parse import quote_plus

from services.preprocessing_service import ProcessedInput


def _to_list(value: object) -> List[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, str):
        return [value]
    return []


def _project_text(project: Dict) -> str:
    return " ".join(
        [
            str(project.get("title", "")),
            str(project.get("description", "")),
            str(project.get("summary", "")),
            str(project.get("full_text", "")),
            " ".join(_to_list(project.get("domain", []))),
            " ".join(_to_list(project.get("skills", []))),
        ]
    ).strip()


Archetype = Literal[
    "fraud_anomaly",
    "hr_hiring_analytics",
    "jobs_salary_analytics",
    "crime_justice_analytics",
    "health_risk_prediction",
    "cv_medical_screening",
    "nlp_trend_summarization",
    "nlp_text_classification",
    "time_series_forecasting",
    "generic_predictive",
]


def _variation_index(seed: str, n: int) -> int:
    if n <= 0:
        return 0
    return sum(ord(c) for c in seed) % n if seed else 0


def _domain_theme(project: Dict, user_input: ProcessedInput) -> str | None:
    """Broad industry theme from sector, domains, catalog text, and interests."""
    blob = " ".join(
        [
            _project_text(project),
            user_input.interests or "",
            str(project.get("sector", "")),
            " ".join(_to_list(project.get("domain", []))),
        ]
    ).lower()

    def _has_term(term: str) -> bool:
        t = term.strip().lower()
        if len(t) < 2:
            return False
        if " " in t:
            return t in blob
        return re.search(rf"\b{re.escape(t)}\b", blob) is not None

    checks: List[tuple[str, tuple[str, ...]]] = [
        ("health", ("health", "healthcare", "clinical", "patient", "medical", "diabetes", "hospital", "icu")),
        ("finance", ("finance", "financial", "banking", "credit", "investment", "loan", "trading", "fintech")),
        ("agriculture", ("agriculture", "agronomy", "crop", "yield", "farm", "soil", "irrigation", "harvest")),
        ("education", ("education", "student", "edtech", "academic", "learning", "university", "school", "course")),
        # Avoid "style" (matches "Production-style", etc.) and loose "retail".
        ("fashion", ("fashion", "apparel", "garment", "boutique", "runway", "lookbook", "couture")),
        ("cybersecurity", ("cybersecurity", "intrusion", "malware", "firewall", "phishing", "siem")),
        ("environment", ("environment", "climate", "wildfire", "carbon", "pollution", "sustainability", "weather")),
        ("iot", ("iot", "sensor", "embedded", "mqtt", "edge", "telemetry")),
    ]
    for name, keys in checks:
        if any(_has_term(k) for k in keys):
            return name
    if _has_term("cyber") and _has_term("security"):
        return "cybersecurity"
    return None


def _archetype_hint_key(project: Dict) -> str:
    h = str(project.get("archetype_hint", "")).strip().lower()
    allowed = (
        "generic_predictive",
        "time_series_forecasting",
        "nlp_text_classification",
        "nlp_trend_summarization",
        "cv_medical_screening",
        "fraud_anomaly",
    )
    return h if h in allowed else "generic_predictive"


def _catalog_use_case_is_boilerplate(use_case: str) -> bool:
    u = use_case.lower().strip()
    if not u.startswith("build a "):
        return False
    return any(x in u for x in ("dashboard", "forecasting", "triage", "pipeline", "monitor", "complaints"))


def _infer_archetype(project: Dict, user_input: ProcessedInput) -> Archetype:
    hint = str(project.get("archetype_hint", "")).strip().lower()
    if hint in (
        "fraud_anomaly",
        "time_series_forecasting",
        "nlp_text_classification",
        "nlp_trend_summarization",
        "cv_medical_screening",
        "generic_predictive",
    ):
        return cast(Archetype, hint)

    text = _project_text(project).lower()
    title = str(project.get("title", "")).lower()
    interest = (user_input.interests or "").lower()

    if any(k in text for k in ["fraud", "anomaly", "chargeback", "money laundering"]):
        return "fraud_anomaly"
    if any(k in text for k in ["hiring", "recruit", "resume", "candidate", "applicant", "hr"]):
        return "hr_hiring_analytics"
    if any(k in text for k in ["salary", "salaries", "jobs", "glassdoor", "compensation"]):
        return "jobs_salary_analytics"
    if any(k in text for k in ["crime", "justice", "police", "offense", "court", "recidiv"]):
        return "crime_justice_analytics"
    if any(k in text for k in ["breast cancer", "mammogram", "x-ray", "xray", "tumor", "lesion"]) or "computer vision" in text:
        return "cv_medical_screening"
    if any(k in text for k in ["diabetes", "sepsis", "stroke", "risk prediction", "patient", "clinical"]) or "health" in interest:
        return "health_risk_prediction"
    if any(k in text for k in ["time series", "forecast", "forecasting", "temporal", "trend over time"]):
        return "time_series_forecasting"
    if any(k in text for k in ["survey", "reviews", "sentiment", "text classification", "spam", "toxicity"]) and any(
        k in text for k in ["text", "nlp", "review", "tweet", "comment"]
    ):
        return "nlp_text_classification"
    if any(k in text for k in ["the rise of", "report", "articles", "news", "analysis"]) and any(
        k in text for k in ["nlp", "text", "article", "news", "report"]
    ):
        return "nlp_trend_summarization"

    # Fall back on domain hints.
    domain = " ".join(_to_list(project.get("domain", []))).lower()
    if "computer vision" in domain:
        return "cv_medical_screening"
    if "nlp" in domain:
        return "nlp_trend_summarization"
    if "data science" in domain:
        return "jobs_salary_analytics" if "job" in title else "generic_predictive"
    return "generic_predictive"


def _clean_phrase(s: str) -> str:
    s = re.sub(r"\s+", " ", (s or "").strip())
    return s


def _kaggle_search_link(query: str) -> str:
    q = _clean_phrase(query)
    if not q:
        return ""
    return f"https://www.kaggle.com/search?q={quote_plus(q)}"


def _strip_source_required_suffix(name: str) -> str:
    n = _clean_phrase(name)
    n = re.sub(r"\s*\(source required\)\s*$", "", n, flags=re.IGNORECASE).strip()
    return n


def _is_concrete_dataset_url(link: str) -> bool:
    return bool(re.search(r"kaggle\.com/(?:datasets/|c/|competitions/)", link, re.IGNORECASE))


_SYNTHETIC_DATASET_NAME = re.compile(
    r"(?i)\b(complaint|incidents?|operational logs|metrics time series|demand forecasting|"
    r"feedback text|cctv|surveillance|fraud|transaction|anomalies?|seasonality)\w*\s+dataset\s*$"
)


def _is_synthetic_dataset_label(name: str) -> bool:
    n = (name or "").strip().lower()
    if not n:
        return True
    if "source required" in n:
        return True
    if _SYNTHETIC_DATASET_NAME.search(n):
        return True
    return False


# Verified Kaggle dataset/competition pages (concrete URLs, not search).
_STARTER_INDUSTRIAL_IOT: List[Tuple[str, str]] = [
    (
        "Machine Predictive Maintenance Classification",
        "https://www.kaggle.com/datasets/shivamb/machine-predictive-maintenance-classification",
    ),
    (
        "Quality Prediction in Mining Process",
        "https://www.kaggle.com/datasets/edumagalhaes/quality-prediction-in-a-mining-process",
    ),
]
_STARTER_NLP: List[Tuple[str, str]] = [
    ("IMDB Dataset of 50K Movie Reviews", "https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews"),
    ("SMS Spam Collection Dataset", "https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset"),
    ("A Million News Headlines (ABC Australia)", "https://www.kaggle.com/datasets/therohk/million-headlines"),
]
_STARTER_CV: List[Tuple[str, str]] = [
    ("Intel Image Classification", "https://www.kaggle.com/datasets/puneet6060/intel-image-classification"),
    ("Cats vs Dogs", "https://www.kaggle.com/c/dogs-vs-cats-redux-kernels-edition"),
]
_STARTER_SERIES: List[Tuple[str, str]] = [
    ("Store Sales Time Series", "https://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting"),
    ("Air Passengers (via TensorFlow)", "https://www.tensorflow.org/datasets/catalog/airpassengers"),
]
_STARTER_FRAUD: List[Tuple[str, str]] = [
    ("Credit Card Fraud Detection", "https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud"),
    ("IEEE-CIS Fraud Detection", "https://www.kaggle.com/c/ieee-fraud-detection"),
]
_STARTER_GENERAL: List[Tuple[str, str]] = [
    ("Titanic", "https://www.kaggle.com/c/titanic"),
    ("House Prices: Advanced Regression Techniques", "https://www.kaggle.com/c/house-prices-advanced-regression-techniques"),
    ("Pima Indians Diabetes Database", "https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database"),
    ("California Housing Prices", "https://www.kaggle.com/datasets/camnugent/california-housing-prices"),
]


def _starter_pool_for_project(project: Dict) -> List[Tuple[str, str]]:
    blob = (_project_text(project) + " " + str(project.get("sector", ""))).lower()
    domains = " ".join(_to_list(project.get("domain", []))).lower()
    hint = str(project.get("archetype_hint", "")).lower()

    if any(x in blob for x in ("robot", "robotic", "industrial", "manufacturing", "automation")):
        return _STARTER_INDUSTRIAL_IOT
    if hint == "fraud_anomaly" or any(x in blob for x in ("fraud", "anomaly", "chargeback")):
        return _STARTER_FRAUD
    if hint == "time_series_forecasting" or "forecast" in blob:
        return _STARTER_SERIES
    if hint == "cv_medical_screening" or "computer vision" in domains or "vision" in domains:
        return _STARTER_CV
    if hint == "nlp_text_classification" or "nlp" in domains or "nlp" in blob:
        return _STARTER_NLP
    return _STARTER_GENERAL


def _pick_starter_dataset(project: Dict, seed_extra: str = "") -> Tuple[str, str]:
    pool = _starter_pool_for_project(project)
    seed = f"{project.get('title', '')}|{project.get('sector', '')}|{seed_extra}"
    idx = sum(ord(c) for c in seed) % len(pool)
    return pool[idx]


def _resolve_dataset_fields(project: Dict) -> Tuple[str, str]:
    """Return (dataset_name, dataset_link); prefer real dataset pages over search URLs or template labels."""
    raw_name = str(project.get("dataset_name", "")).strip()
    link = str(project.get("dataset_link", "")).strip()
    cleaned = _strip_source_required_suffix(raw_name)
    display = cleaned or str(project.get("title", "Dataset")).strip() or "Dataset"

    queries = project.get("dataset_queries")
    query0 = ""
    if isinstance(queries, list) and queries:
        query0 = _clean_phrase(str(queries[0]))

    opts = project.get("dataset_options")
    if isinstance(opts, list):
        for o in opts:
            if not isinstance(o, dict):
                continue
            ol = str(o.get("link", "")).strip()
            on = str(o.get("name", "")).strip()
            if ol and _is_concrete_dataset_url(ol) and not _is_synthetic_dataset_label(on or display):
                return (on or display), ol

    if link and _is_concrete_dataset_url(link) and not _is_synthetic_dataset_label(display):
        return display, link

    # Template names like "Robotics complaint dataset" are not real datasets; map to a concrete starter.
    if _is_synthetic_dataset_label(display) or ("kaggle.com/search" in link):
        return _pick_starter_dataset(project, seed_extra=query0 or raw_name)

    if not link:
        if _is_synthetic_dataset_label(display):
            return _pick_starter_dataset(project, seed_extra=query0 or raw_name)
        return display, _kaggle_search_link(query0 or display)

    if link and _is_concrete_dataset_url(link):
        return display, link

    return display, link


# Domain-aware copy when the catalog template is generic (reduces “same dashboard” feel).
_DOMAIN_TITLE_TEMPLATES: Dict[tuple[str, str], tuple[str, ...]] = {
    ("health", "generic_predictive"): (
        "Clinical operations analytics & triage support for {sector}",
        "Patient risk stratification and decision support in {sector}",
    ),
    ("health", "time_series_forecasting"): (
        "Healthcare demand and capacity forecasting for {sector}",
        "Clinical workflow load prediction for {sector}",
    ),
    ("health", "nlp_text_classification"): (
        "Clinical notes and intake text analytics for {sector}",
        "Safety and quality signals from healthcare text in {sector}",
    ),
    ("finance", "generic_predictive"): (
        "Financial risk scoring and monitoring for {sector}",
        "Credit and exposure analytics for {sector}",
    ),
    ("finance", "fraud_anomaly"): (
        "Fraud detection and case prioritization for {sector}",
        "Anomaly surveillance for financial operations in {sector}",
    ),
    ("finance", "time_series_forecasting"): (
        "Market and liquidity forecasting workspace for {sector}",
        "Financial time-series planning dashboard for {sector}",
    ),
    ("agriculture", "generic_predictive"): (
        "Farm advisory and yield intelligence for {sector}",
        "Agri operations dashboard with agronomic signals for {sector}",
    ),
    ("agriculture", "time_series_forecasting"): (
        "Seasonal yield and input planning forecasts for {sector}",
        "Climate-aware production forecasting for {sector}",
    ),
    ("agriculture", "cv_medical_screening"): (
        "Crop and field vision analytics for {sector}",
        "Computer vision for crop health in {sector}",
    ),
    ("education", "generic_predictive"): (
        "Student success analytics and early alerts for {sector}",
        "Learning analytics and performance insights for {sector}",
    ),
    ("education", "nlp_text_classification"): (
        "Feedback and discourse analytics for {sector}",
        "Text-based academic support triage for {sector}",
    ),
    ("fashion", "generic_predictive"): (
        "Merchandising and assortment intelligence for {sector}",
        "Retail analytics and trend signals for {sector}",
    ),
    ("fashion", "nlp_text_classification"): (
        "Reviews and social text for fashion demand in {sector}",
        "NLP-driven style and sentiment insights for {sector}",
    ),
    ("cybersecurity", "generic_predictive"): (
        "Security operations analytics for {sector}",
        "Threat prioritization and SOC decision support for {sector}",
    ),
    ("cybersecurity", "fraud_anomaly"): (
        "Network intrusion and anomaly response for {sector}",
        "Security event triage with calibrated risk scores for {sector}",
    ),
    ("environment", "generic_predictive"): (
        "Environmental monitoring and impact analytics for {sector}",
        "Climate and resource risk dashboard for {sector}",
    ),
    ("environment", "time_series_forecasting"): (
        "Environmental forecasting and scenario planning for {sector}",
        "Long-horizon ecosystem or hazard trends for {sector}",
    ),
    ("environment", "cv_medical_screening"): (
        "Remote sensing and vision for environmental ops in {sector}",
        "Geospatial vision analytics for {sector}",
    ),
    ("iot", "generic_predictive"): (
        "IoT telemetry analytics and alerting for {sector}",
        "Edge-to-cloud intelligence for {sector}",
    ),
    ("iot", "time_series_forecasting"): (
        "Predictive maintenance and signal forecasting for {sector}",
        "Sensor stream forecasting for {sector}",
    ),
}

# When no industry theme matches, still diversify by catalog archetype hint.
_HINT_FALLBACK_TITLES: Dict[str, tuple[str, ...]] = {
    "nlp_text_classification": (
        "Operational text triage and NLP analytics for {sector}",
        "Language-driven insights and routing for {sector}",
        "NLP operations cockpit for {sector}",
        "Text intelligence workflow for {sector}",
    ),
    "nlp_trend_summarization": (
        "Narrative intelligence and trend radar for {sector}",
        "Text-centric insight explorer for {sector}",
    ),
    "time_series_forecasting": (
        "Forecasting and scenario lab for {sector}",
        "Temporal analytics workbench for {sector}",
    ),
    "cv_medical_screening": (
        "Vision analytics and monitoring for {sector}",
        "Image-driven screening prototype for {sector}",
    ),
    "fraud_anomaly": (
        "Risk and anomaly operations center for {sector}",
        "Surveillance analytics for {sector}",
    ),
    "generic_predictive": (
        "Decision intelligence prototype for {sector}",
        "Data-driven operations cockpit for {sector}",
    ),
}


def _hint_fallback_title(project: Dict) -> str | None:
    hint = _archetype_hint_key(project)
    sector = _clean_phrase(str(project.get("sector", ""))) or "this domain"
    pool = _HINT_FALLBACK_TITLES.get(hint)
    if not pool:
        return None
    idx = _variation_index(str(project.get("title", "")) + hint, len(pool))
    return pool[idx].format(sector=sector)

_DOMAIN_PROBLEM: Dict[str, str] = {
    "health": "Improve care delivery by turning operational and clinical signals into timely, explainable decisions.",
    "finance": "Reduce exposure and speed up decisions by scoring risk, surfacing anomalies, and supporting auditable reviews.",
    "agriculture": "Support better yields and lower waste by combining field data, weather-style signals, and transparent models.",
    "education": "Improve outcomes by spotting at-risk learners early and recommending fair, explainable interventions.",
    "fashion": "Align assortment and demand by blending catalog signals, text/reviews, and similarity-aware recommendations.",
    "cybersecurity": "Prioritize real threats faster with calibrated scores, evidence trails, and analyst-friendly workflows.",
    "environment": "Make environmental risk visible early with monitoring, forecasting, and scenario-ready dashboards.",
    "iot": "Turn device telemetry into reliable predictions, alerts, and closed-loop actions at the edge or in the cloud.",
}


def _themed_catalog_title(project: Dict, theme: str | None) -> str | None:
    sector = _clean_phrase(str(project.get("sector", ""))) or "this domain"
    hint = _archetype_hint_key(project)
    templates: tuple[str, ...] | None = None
    if theme:
        templates = _DOMAIN_TITLE_TEMPLATES.get((theme, hint)) or _DOMAIN_TITLE_TEMPLATES.get(
            (theme, "generic_predictive")
        )
    if not templates:
        return _hint_fallback_title(project)
    idx = _variation_index(str(project.get("title", "")) + (theme or "") + hint, len(templates))
    return templates[idx].format(sector=sector)


def _domain_description_lede(
    theme: str | None,
    primary_domain: str,
    dataset_name: str,
    user_input: ProcessedInput,
    project: Dict,
) -> str:
    interest = user_input.interests or "your stated goals"
    if theme == "health":
        return (
            f"Shape a {primary_domain.lower()} health analytics build around '{dataset_name}', focused on safe, "
            f"interpretable decisions aligned with {interest}."
        )
    if theme == "finance":
        return (
            f"Design a {primary_domain.lower()} risk and decision workflow using '{dataset_name}', with metrics "
            f"that matter for compliance and stakeholders tied to {interest}."
        )
    if theme == "agriculture":
        return (
            f"Build an agronomy-aware analytics path on '{dataset_name}' that turns signals into guidance "
            f"relevant to {interest}."
        )
    if theme == "education":
        return (
            f"Create an education analytics prototype on '{dataset_name}' that balances accuracy and fairness "
            f"for goals around {interest}."
        )
    if theme == "fashion":
        return (
            f"Assemble a fashion/retail intelligence slice on '{dataset_name}'—from features to recommendations—"
            f"grounded in {interest}."
        )
    if theme == "cybersecurity":
        return (
            f"Stand up a security-analytics workflow on '{dataset_name}' with traceable evidence and analyst-ready "
            f"outputs for {interest}."
        )
    if theme == "environment":
        return (
            f"Model environmental signals from '{dataset_name}' into forecasts and dashboards that support planning "
            f"around {interest}."
        )
    if theme == "iot":
        return (
            f"Connect streaming or device data from '{dataset_name}' to predictions and alerts that fit {interest}."
        )
    dom = primary_domain.lower()
    variants = [
        f"Build a {dom} project grounded in open data ('{dataset_name}') to address your interest in {interest}.",
        f"Prototype a {dom} pipeline using '{dataset_name}' as your initial data anchor, aligned with {interest}.",
        f"Structure a {dom} capstone around '{dataset_name}' while keeping goals tied to {interest}.",
        f"Ship a {dom} proof-of-concept on '{dataset_name}' with clear metrics that reflect {interest}.",
    ]
    idx = _variation_index(str(project.get("title", "")) + (user_input.semantic_query or ""), len(variants))
    return variants[idx]


def _domain_steps_generic_predictive(theme: str, dataset_name: str, interest_snippet: str) -> List[str] | None:
    d, i = dataset_name, interest_snippet or "your use case"
    if theme == "health":
        return [
            f"Define clinical/operational outcomes and label strategy using '{d}' (with privacy and governance guardrails).",
            f"Engineer features that clinicians or ops staff can interpret; document missingness and cohort bias for {i}.",
            "Train calibrated classifiers or risk models; report precision/recall at clinically meaningful thresholds.",
            "Add explainability (SHAP-style drivers) and a review workflow so humans can override confidently.",
            "Ship a Flask-backed dashboard prototype with audit logs and a retraining checklist.",
        ]
    if theme == "finance":
        return [
            f"Clean and validate '{d}'; engineer financial features with strict leakage checks for {i}.",
            "Train baseline linear models plus tree ensembles (e.g. gradient boosting); tune for PR-AUC where imbalance matters.",
            "Calibrate probabilities and pick thresholds with explicit cost tradeoffs for analysts.",
            "Expose scores through a small API and a decision-support UI with drill-down to contributing factors.",
            "Document monitoring: population drift, feature stability, and periodic backtests.",
        ]
    if theme == "agriculture":
        return [
            f"Profile '{d}' across seasons, regions, or crops; align targets with agronomic questions for {i}.",
            "Build features for weather/soil/categorical agronomic signals; validate with domain sanity checks.",
            "Compare interpretable models vs boosted trees for yield or risk targets; stress-test edge cases.",
            "Package recommendations (what to plant, irrigate, or inspect) with uncertainty where possible.",
            "Deliver a farmer-facing or advisor demo plus a short field-trial validation plan.",
        ]
    if theme == "education":
        return [
            f"Clarify prediction targets and fairness constraints for '{d}' tied to {i} (e.g. early alert vs recommendation).",
            "Preprocess academic/behavioral features; check for leakage from future information.",
            "Train models and evaluate subgroup metrics; document fairness limitations transparently.",
            "Build an advisor/instructor UI surfacing top drivers and suggested interventions.",
            "Add a bias review section and a plan for human oversight before high-stakes use.",
        ]
    if theme == "fashion":
        return [
            f"Ingest '{d}' (tabular, text, or images as available) and define similarity or ranking tasks for {i}.",
            "Build embeddings or feature pipelines suited to modality; evaluate with ranking/hit-rate style checks.",
            "Train a recommender or trend classifier with cold-start fallbacks.",
            "Ship a lightweight catalog or outfit explorer demo backed by Flask.",
            "Summarize evaluation, limitations, and how you would run periodic refresh jobs.",
        ]
    if theme == "cybersecurity":
        return [
            f"Normalize '{d}' into security events; define attack/benign labels and realistic baselines for {i}.",
            "Handle severe class imbalance; optimize PR-AUC and calibrated alert rates.",
            "Compare rules + ML ensembles; add analyst-facing explanations for top alerts.",
            "Prototype a SOC-style triage view with evidence links back to raw fields.",
            "Outline purple-team validation and continuous retraining triggers.",
        ]
    if theme == "environment":
        return [
            f"Frame prediction or monitoring goals for '{d}' (hazard, exposure, or resource) aligned with {i}.",
            "Build geospatial or temporal features where relevant; document data gaps openly.",
            "Train models with proper spatial/temporal splits to avoid optimistic scores.",
            "Visualize risk layers and scenarios in a dashboard stakeholders can interpret.",
            "Add a limitations section on climate/scale assumptions and data freshness.",
        ]
    if theme == "iot":
        return [
            f"Model the signal topology for '{d}' and ingestion path (batch vs stream) for {i}.",
            "Engineer windowed features; detect anomalies and forecast key telemetry channels.",
            "Deploy scoring near the edge or via API; measure latency and failure modes.",
            "Build alerting with suppression rules to reduce alert fatigue.",
            "Document device security, firmware update strategy, and observability.",
        ]
    return None


def _domain_tech_addons(theme: str | None, archetype: Archetype) -> List[str]:
    if not theme:
        return []
    out: List[str] = []
    if theme == "finance" or archetype == "fraud_anomaly":
        out.extend(["XGBoost", "Pandas"])
    if theme == "health":
        out.extend(["Pandas", "imbalanced-learn"])
    if theme == "fashion" and archetype in ("nlp_text_classification", "nlp_trend_summarization", "cv_medical_screening"):
        out.append("Sentence-Transformers")
    if theme == "cybersecurity":
        out.extend(["Pandas", "scikit-learn"])
    if theme == "iot":
        out.extend(["InfluxDB or SQLite", "FastAPI"])
    if theme == "agriculture":
        out.extend(["GeoPandas", "Matplotlib"])
    if theme == "education":
        out.append("Fairlearn")
    dedup: List[str] = []
    for x in out:
        if x not in dedup:
            dedup.append(x)
    return dedup[:4]


def _make_problem_statement(project: Dict, user_input: ProcessedInput) -> str:
    # Convert dataset-style descriptions into a real project problem statement.
    idea = project.get("project_idea")
    if isinstance(idea, dict):
        use_case = str(idea.get("use_case", "")).strip()
        if use_case:
            theme = _domain_theme(project, user_input)
            if (
                theme
                and _catalog_use_case_is_boilerplate(use_case)
                and _infer_archetype(project, user_input) == "generic_predictive"
                and theme in _DOMAIN_PROBLEM
            ):
                return _DOMAIN_PROBLEM[theme]
            return use_case.rstrip(".") + "."

    description = _clean_phrase(str(project.get("description", "")))
    interest = _clean_phrase(user_input.interests)
    archetype = _infer_archetype(project, user_input)

    if archetype == "fraud_anomaly":
        return "Reduce financial losses by detecting suspicious transactions early and routing high-risk cases for review."
    if archetype == "jobs_salary_analytics":
        return "Help students or job seekers make better career decisions by forecasting salary ranges and identifying high-demand skills."
    if archetype == "hr_hiring_analytics":
        return "Improve screening quality by ranking candidates consistently while keeping the system fair, transparent, and auditable."
    if archetype == "crime_justice_analytics":
        return "Support public safety planning by analysing patterns in incidents and producing risk-informed, explainable insights."
    if archetype == "cv_medical_screening":
        return "Assist clinicians by triaging medical images and flagging cases that need urgent review, with interpretable visual evidence."
    if archetype == "health_risk_prediction":
        return "Enable earlier intervention by predicting patient risk and highlighting the strongest contributing factors."
    if archetype == "nlp_trend_summarization":
        return "Turn unstructured text into actionable summaries and trends so decision makers can understand what is changing and why."

    if description and len(description) >= 24 and "dataset" not in description.lower():
        return description[0].upper() + description[1:]
    theme = _domain_theme(project, user_input)
    if theme and archetype == "generic_predictive" and theme in _DOMAIN_PROBLEM:
        return _DOMAIN_PROBLEM[theme]
    if user_input.interests:
        return f"Develop a practical solution for {interest} using real-world data and measurable outcomes."
    return "Build a data-driven solution for a real-world prediction or decision problem."


def _make_project_title(project: Dict, user_input: ProcessedInput) -> str:
    idea = project.get("project_idea")
    theme = _domain_theme(project, user_input)
    if isinstance(idea, dict):
        use_case = str(idea.get("use_case", "")).strip()
        if use_case:
            if _catalog_use_case_is_boilerplate(use_case):
                themed = _themed_catalog_title(project, theme)
                if themed:
                    return themed
            # Convert "X using Y" into a clean, project-first title
            use_case = re.sub(r"\s+using\s+.*$", "", use_case, flags=re.I).strip().strip(".")
            if len(use_case) >= 8:
                return use_case

    base_title = str(project.get("title", "Project")).strip()
    interest = user_input.interests.strip()
    if interest:
        interest = interest.split(",")[0].strip().title()
    if "dataset" in base_title.lower():
        base_title = base_title.replace("Dataset", "").strip(" -")
    if "prediction" in _project_text(project).lower():
        return f"AI-Based {base_title} Prediction System"
    if interest:
        return f"{interest} Intelligent Project: {base_title}"
    return f"Applied AI Project: {base_title}"


def _tech_stack(project: Dict, user_input: ProcessedInput, matched_skills: List[str]) -> List[str]:
    stack: List[str] = []
    stack.extend([skill.title() for skill in matched_skills[:3]])
    archetype = _infer_archetype(project, user_input)
    theme = _domain_theme(project, user_input)
    stack.extend(_domain_tech_addons(theme, archetype))
    domains = [d.lower() for d in _to_list(project.get("domain", []))]
    if any(domain in domains for domain in ["machine learning", "artificial intelligence", "data science", "nlp", "computer vision"]):
        stack.extend(["Python", "Scikit-learn"])
    if "web development" in domains:
        stack.extend(["Flask", "React"])
    if "mobile development" in domains:
        stack.extend(["Flutter"])
    if "iot" in domains:
        stack.extend(["MQTT"])
    if user_input.preferred_project_type == "research":
        stack.extend(["Jupyter", "Matplotlib"])
    if user_input.preferred_project_type == "application":
        stack.extend(["Flask API"])
    deduped: List[str] = []
    for item in stack:
        if item and item not in deduped:
            deduped.append(item)
    return deduped[:6] if deduped else ["Python", "Flask", "Scikit-learn"]


def _implementation_steps(
    project: Dict,
    user_input: ProcessedInput,
    dataset_name: str,
    primary_domain: str,
) -> List[str]:
    level = user_input.experience_level or "intermediate"
    domains = [d.lower() for d in _to_list(project.get("domain", []))]
    project_type = user_input.preferred_project_type
    interest_snippet = (user_input.interests or primary_domain).strip()

    # Application‑centric projects (dashboards, web apps around the model)
    if project_type == "application" or "web development" in domains:
        steps = [
            f"Step 1: Define the concrete use-cases for your {primary_domain.lower()} app (for example, how a user interacts with {interest_snippet}).",
            f"Step 2: Design the data schema and REST API that will serve predictions or insights derived from the '{dataset_name}' data.",
            "Step 3: Build a clean dashboard or web interface that surfaces only the most important metrics and actions.",
            f"Step 4: Train an ML model on the '{dataset_name}' dataset and connect it to the API endpoints powering the UI.",
            "Step 5: Add authentication, basic monitoring, and deploy the app (Flask + cloud hosting) so others can try it.",
        ]
    # Hardware / IoT oriented projects
    elif project_type == "system" or "iot" in domains:
        steps = [
            f"Step 1: Decide which physical signals you want to observe for your {interest_snippet} scenario and sketch the sensor/microcontroller layout.",
            "Step 2: Implement firmware or edge logic to collect, buffer, and transmit readings to your backend reliably.",
            f"Step 3: Store the incoming stream so you can periodically align it with offline patterns learned from '{dataset_name}'.",
            "Step 4: Build a small monitoring or control dashboard to visualise states and trigger alerts or actions.",
            "Step 5: Evaluate latency, reliability, and safety and write up how the full edge→cloud pipeline works.",
        ]
    # Research‑oriented explorations
    elif project_type == "research":
        steps = [
            f"Step 1: Perform a short literature review on {interest_snippet or 'similar datasets'} and identify 1–2 strong baselines.",
            f"Step 2: Implement a clean data pipeline for '{dataset_name}' and faithfully reproduce at least one baseline result.",
            "Step 3: Design and implement one or two novel variations (new features, architectures, or training regimes).",
            "Step 4: Run controlled experiments, report metrics, and analyse failure cases and limitations in detail.",
            "Step 5: Summarise findings in a short paper-style report with plots, tables, and ablation studies.",
        ]
    # Default: infer a topic-specific ML archetype and generate a plan that matches it
    else:
        archetype = _infer_archetype(project, user_input)
        theme = _domain_theme(project, user_input)
        steps: List[str] | None = None
        if archetype == "generic_predictive" and theme:
            steps = _domain_steps_generic_predictive(theme, dataset_name, interest_snippet)
        if steps is None:
            if archetype == "fraud_anomaly":
                steps = [
                    f"Step 1: Define what 'fraud' means for your use-case and label strategy using '{dataset_name}' (chargebacks, confirmed fraud, suspicious patterns).",
                    "Step 2: Handle class imbalance properly (stratified splits, PR-AUC, cost-sensitive thresholds).",
                    "Step 3: Train models suited for fraud signals (tree ensembles + calibrated probabilities) and compare with an anomaly baseline.",
                    "Step 4: Build an investigator workflow: rules + model scores, top reasons per flag, and feedback capture for retraining.",
                    "Step 5: Stress-test against drift and adversarial behavior; document monitoring signals and retraining triggers.",
                ]
            elif archetype == "jobs_salary_analytics":
                steps = [
                    f"Step 1: Define 2–3 concrete questions from '{dataset_name}' (salary prediction, skill→salary lift, role clustering).",
                    "Step 2: Build a feature pipeline from skills, location, seniority, and company signals; validate with leakage checks.",
                    "Step 3: Train regression models for salary ranges and add uncertainty estimates (intervals) so outputs are honest.",
                    "Step 4: Create an insights layer: top skills by role, geographic differences, and trend dashboards for students.",
                    "Step 5: Deliver as an interactive career dashboard + report with clear recommendations and limitations.",
                ]
            elif archetype == "hr_hiring_analytics":
                steps = [
                    f"Step 1: Define ranking criteria for candidates using '{dataset_name}' and decide what your model is allowed to use.",
                    "Step 2: Build a scoring model and an explanation layer (why shortlisted / why rejected) with audit logs.",
                    "Step 3: Add fairness checks (subgroup performance, bias probes) and mitigation steps you can justify.",
                    "Step 4: Create a recruiter UI: shortlist view, evidence panel, and feedback loop to correct wrong suggestions.",
                    "Step 5: Write an evaluation section that balances accuracy, fairness, and usability with concrete examples.",
                ]
            elif archetype == "crime_justice_analytics":
                steps = [
                    f"Step 1: Convert '{dataset_name}' into an analysis-ready incident schema (time, location, type, severity) and define outputs.",
                    "Step 2: Build spatiotemporal features and segment the problem (hotspot detection, risk forecasting, resource planning).",
                    "Step 3: Train a predictive model (or forecasting model) and validate on time-based splits to avoid leakage.",
                    "Step 4: Add interpretability: what drives risk, what changes predictions, and clear warnings about misuse.",
                    "Step 5: Ship a policy dashboard: hotspot map, trend charts, and scenario planning with guardrails.",
                ]
            elif archetype == "cv_medical_screening":
                steps = [
                    f"Step 1: Curate image splits for '{dataset_name}' and define the clinical-style question (triage, screening, severity).",
                    "Step 2: Build a vision pipeline (augmentation + preprocessing) and train a strong baseline (CNN/transfer learning).",
                    "Step 3: Evaluate with sensitivity-focused metrics and choose an operating point appropriate for screening.",
                    "Step 4: Add explainability (Grad-CAM style heatmaps) and failure-case galleries to build trust.",
                    "Step 5: Package a clinician-style demo: upload image → prediction + confidence + explanation.",
                ]
            elif archetype == "health_risk_prediction":
                steps = [
                    f"Step 1: Define the risk outcome you want to predict using '{dataset_name}' and what intervention it enables.",
                    "Step 2: Build clinically-plausible features and validate for leakage and missingness patterns.",
                    "Step 3: Train calibrated models and evaluate tradeoffs (false negatives vs false positives) with threshold selection.",
                    "Step 4: Produce patient-level explanations and cohort-level insights (risk drivers, segment behavior).",
                    "Step 5: Deliver a decision-support prototype: risk score, top drivers, and recommended next steps.",
                ]
            elif archetype == "nlp_text_classification":
                steps = [
                    f"Step 1: Define labels and acceptable failure modes for '{dataset_name}' (precision vs recall tradeoffs).",
                    "Step 2: Build a text preprocessing + tokenization pipeline; create stratified train/val/test splits.",
                    "Step 3: Train baselines (logistic regression on TF-IDF) then stronger models; tune thresholds on validation data.",
                    "Step 4: Add an explanation layer (top tokens/phrases) and a manual review queue for low-confidence items.",
                    "Step 5: Deploy a Flask API + simple UI for batch scoring and exportable audit logs.",
                ]
            elif archetype == "nlp_trend_summarization":
                steps = [
                    f"Step 1: Assemble the text corpus from '{dataset_name}' and define the outputs (summaries, themes, trend shifts).",
                    "Step 2: Build an NLP pipeline (cleaning, deduping, embeddings) and generate topic clusters over time.",
                    "Step 3: Create extractive summaries per topic and a timeline view of how themes rise/fall.",
                    "Step 4: Add a search + evidence panel so every insight links back to the exact source documents.",
                    "Step 5: Ship an interactive 'insight explorer' dashboard with topics, summaries, and drill-down examples.",
                ]
            elif archetype == "time_series_forecasting":
                steps = [
                    f"Step 1: Define the forecasting horizon and target using '{dataset_name}' and create proper time-based splits.",
                    "Step 2: Build lag/rolling features and strong baselines (seasonal naive, ARIMA-style, gradient boosting).",
                    "Step 3: Train forecasting models and evaluate with business-aligned metrics (MAE/MAPE) and interval coverage.",
                    "Step 4: Diagnose errors by segment and season; add anomaly flags for unusual spikes or drops.",
                    "Step 5: Deliver a forecasting dashboard with scenarios and confidence bands, plus retraining cadence.",
                ]
            else:
                steps = [
                    f"Step 1: Translate your interest in {interest_snippet} into a measurable target using fields from '{dataset_name}'.",
                    "Step 2: Build a repeatable preprocessing pipeline with validation checks and leakage prevention.",
                    "Step 3: Train and tune a small model suite (linear + tree-based) and pick based on performance + interpretability.",
                    "Step 4: Do error analysis by segment and write down where the model fails and why.",
                    "Step 5: Deliver a simple demo (API or dashboard) that makes the prediction useful to an end user.",
                ]

    # Adjust modelling depth based on experience level where relevant.
    if level == "beginner":
        steps[2] = steps[2].replace("advanced models, ", "").replace("tree‑based models with linear models and ", "")
    elif level == "advanced" and "Train" in steps[2]:
        steps[2] = steps[2] + " Include systematic hyper‑parameter searches and careful regularisation."

    return steps


def build_project_recommendation(
    project: Dict,
    user_input: ProcessedInput,
    matched_skills: List[str],
    recommendation_type: str,
    score: float,
    score_breakdown: Dict,
    feasibility_notes: List[str],
) -> Dict:
    domains = _to_list(project.get("domain", []))
    dataset_name, dataset_link = _resolve_dataset_fields(project)

    reason = (
        f"This idea aligns semantically with your interest in '{user_input.interests or 'applied AI'}', "
        f"uses your strongest skills ({', '.join(matched_skills) if matched_skills else 'foundational ML skills'}), "
        f"and is calibrated for your {user_input.experience_level or 'intermediate'} level and {user_input.time_available or 'medium'} timeline."
    )

    project_text = _project_text(project).lower()
    primary_domain = domains[0] if domains else "Applied AI"
    archetype = _infer_archetype(project, user_input)
    theme = _domain_theme(project, user_input)
    idea = project.get("project_idea") if isinstance(project.get("project_idea"), dict) else {}

    if isinstance(idea, dict) and any(str(idea.get(k, "")).strip() for k in ["industry_context", "deliverables", "deployment_plan"]):
        deliverables = idea.get("deliverables")
        deliverables_txt = ""
        if isinstance(deliverables, list) and deliverables:
            deliverables_txt = " Key deliverables: " + "; ".join(str(x) for x in deliverables[:3]) + "."
        description_body = (
            f"{str(idea.get('industry_context','')).strip()} {deliverables_txt} "
            f"{str(idea.get('deployment_plan','')).strip()}"
        ).strip()
    elif "time series" in project_text:
        description_body = "Design and build a forecasting system that learns temporal patterns from the underlying dataset and surfaces actionable predictions to stakeholders."
    elif "image" in project_text or "computer vision" in project_text:
        description_body = "Create an intelligent vision system that processes images from the dataset to automate classification, detection, or screening tasks in your chosen domain."
    elif "text" in project_text or "nlp" in project_text:
        description_body = "Build an end‑to‑end NLP pipeline that turns raw text from the dataset into structured insights, alerts, or recommendations for users."
    else:
        description_body = (
            "Turn the structured dataset into a practical decision‑support system that ingests real records, "
            "produces reliable predictions, and exposes them through a usable interface."
        )

    return {
        "title": _make_project_title(project, user_input),
        "domain": domains[0] if len(domains) == 1 else domains,
        "problem_statement": _make_problem_statement(project, user_input),
        "project_description": (
            f"{_domain_description_lede(theme, primary_domain, dataset_name, user_input, project)} {description_body}"
        ).strip(),
        "implementation_approach": _implementation_steps(project, user_input, dataset_name, primary_domain),
        "tech_stack": _tech_stack(project, user_input, matched_skills),
        "dataset": {"name": dataset_name, "link": dataset_link},
        "difficulty": str(project.get("difficulty") or "intermediate").strip().title() or "Intermediate",
        "score": round(float(score), 4),
        "archetype": archetype,
        "project_idea": idea if isinstance(idea, dict) else {},
        "matched_skills": matched_skills,
        "score_breakdown": score_breakdown,
        "feasibility_notes": feasibility_notes,
        "reason": reason,
        "type": recommendation_type,
    }
