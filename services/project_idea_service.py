from __future__ import annotations

from typing import Dict, List

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


def _make_problem_statement(project: Dict, user_input: ProcessedInput) -> str:
    description = str(project.get("description", "")).strip()
    if description:
        return description[0].upper() + description[1:]
    if user_input.interests:
        return f"Develop a practical solution for {user_input.interests} using real-world data."
    return "Build a data-driven solution for a real-world prediction or decision problem."


def _make_project_title(project: Dict, user_input: ProcessedInput) -> str:
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


def _implementation_steps(project: Dict, user_input: ProcessedInput) -> List[str]:
    level = user_input.experience_level or "intermediate"
    steps = [
        "Step 1: Ingest dataset and define target variable aligned to the problem statement.",
        "Step 2: Clean and preprocess data (missing values, encoding, scaling, train/validation split).",
        "Step 3: Train baseline and advanced models, then compare with proper metrics.",
        "Step 4: Evaluate model quality, interpret key features, and validate robustness.",
        "Step 5: Package as a deployable prototype (Flask API/dashboard) with usage documentation.",
    ]
    if level == "beginner":
        steps[2] = "Step 3: Start with simple ML models (Logistic Regression/Random Forest) and tune basics."
    elif level == "advanced":
        steps[2] = "Step 3: Build advanced models (ensembles/deep learning) and perform systematic tuning."
    return steps


def build_project_recommendation(
    project: Dict,
    user_input: ProcessedInput,
    matched_skills: List[str],
    recommendation_type: str,
    score: float,
) -> Dict:
    domains = _to_list(project.get("domain", []))
    dataset_link = str(project.get("dataset_link", ""))
    dataset_name = str(project.get("dataset_name", project.get("title", "Recommended Dataset"))).strip()

    reason = (
        f"This idea aligns semantically with your interest in '{user_input.interests or 'applied AI'}', "
        f"uses your strongest skills ({', '.join(matched_skills) if matched_skills else 'foundational ML skills'}), "
        f"and is calibrated for your {user_input.experience_level or 'intermediate'} level and {user_input.time_available or 'medium'} timeline."
    )

    return {
        "title": _make_project_title(project, user_input),
        "domain": domains[0] if len(domains) == 1 else domains,
        "problem_statement": _make_problem_statement(project, user_input),
        "project_description": (
            f"Design and build an end-to-end intelligent system based on '{project.get('title', 'the selected dataset')}'. "
            "The project includes data processing, model development, evaluation, and a deployable prototype."
        ),
        "implementation_approach": _implementation_steps(project, user_input),
        "tech_stack": _tech_stack(project, user_input, matched_skills),
        "dataset": {"name": dataset_name, "link": dataset_link},
        "difficulty": str(project.get("difficulty", "intermediate")),
        "score": round(float(score), 4),
        "reason": reason,
        "type": recommendation_type,
    }
