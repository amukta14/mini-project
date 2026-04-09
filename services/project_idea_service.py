from __future__ import annotations

import re
from typing import Dict, List, Literal

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


def _infer_archetype(project: Dict, user_input: ProcessedInput) -> Archetype:
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


def _make_problem_statement(project: Dict, user_input: ProcessedInput) -> str:
    # Convert dataset-style descriptions into a real project problem statement.
    idea = project.get("project_idea")
    if isinstance(idea, dict):
        use_case = str(idea.get("use_case", "")).strip()
        if use_case:
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
    if user_input.interests:
        return f"Develop a practical solution for {interest} using real-world data and measurable outcomes."
    return "Build a data-driven solution for a real-world prediction or decision problem."


def _make_project_title(project: Dict, user_input: ProcessedInput) -> str:
    idea = project.get("project_idea")
    if isinstance(idea, dict):
        use_case = str(idea.get("use_case", "")).strip()
        if use_case:
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
    dataset_link = str(project.get("dataset_link", ""))
    dataset_name = str(project.get("dataset_name", project.get("title", "Recommended Dataset"))).strip()

    reason = (
        f"This idea aligns semantically with your interest in '{user_input.interests or 'applied AI'}', "
        f"uses your strongest skills ({', '.join(matched_skills) if matched_skills else 'foundational ML skills'}), "
        f"and is calibrated for your {user_input.experience_level or 'intermediate'} level and {user_input.time_available or 'medium'} timeline."
    )

    project_text = _project_text(project).lower()
    primary_domain = domains[0] if domains else "Applied AI"
    archetype = _infer_archetype(project, user_input)
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
            f"Build a {primary_domain.lower()} project that uses the '{dataset_name}' data as a backbone "
            f"to address your interest in {user_input.interests or 'a real-world decision problem'}. "
            f"{description_body}"
        ),
        "implementation_approach": _implementation_steps(project, user_input, dataset_name, primary_domain),
        "tech_stack": _tech_stack(project, user_input, matched_skills),
        "dataset": {"name": dataset_name, "link": dataset_link},
        "difficulty": str(project.get("difficulty", "intermediate")),
        "score": round(float(score), 4),
        "archetype": archetype,
        "project_idea": idea if isinstance(idea, dict) else {},
        "matched_skills": matched_skills,
        "score_breakdown": score_breakdown,
        "feasibility_notes": feasibility_notes,
        "reason": reason,
        "type": recommendation_type,
    }
