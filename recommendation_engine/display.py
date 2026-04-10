"""Human-readable labels for domains and difficulty."""

from __future__ import annotations

from typing import Dict


def format_domain_label(ontology_domain: str) -> str:
    d = ontology_domain.strip().lower()
    acronyms = {
        "nlp": "NLP",
        "iot": "IoT",
        "ar": "AR",
        "vr": "VR",
        "ai": "AI",
    }
    parts = d.split()
    out = []
    for p in parts:
        out.append(acronyms.get(p, p.title()))
    return " ".join(out) if out else ontology_domain.title()


def format_difficulty(project: Dict) -> str:
    raw = str(project.get("difficulty") or "intermediate").strip().lower()
    return raw.title() if raw else "Intermediate"
