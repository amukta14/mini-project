"""75+ domain ontology for labeling and template routing."""

from __future__ import annotations

from typing import Dict, List, Tuple

from services.preprocessing_service import ProcessedInput

# Mandatory ontology (normalized lowercase for matching; display Title Case when needed).
DOMAIN_ONTOLOGY: Tuple[str, ...] = (
    "healthcare",
    "finance",
    "education",
    "agriculture",
    "fashion",
    "sports",
    "transportation",
    "climate",
    "ecommerce",
    "cybersecurity",
    "social media",
    "iot",
    "robotics",
    "energy",
    "real estate",
    "gaming",
    "law",
    "supply chain",
    "marketing",
    "manufacturing",
    "automotive",
    "aerospace",
    "biotechnology",
    "pharmaceuticals",
    "telecommunications",
    "banking",
    "insurance",
    "tourism",
    "hospitality",
    "food industry",
    "nutrition",
    "mental health",
    "fitness",
    "environment",
    "wildlife",
    "geology",
    "astronomy",
    "space tech",
    "blockchain",
    "cryptocurrency",
    "augmented reality",
    "virtual reality",
    "computer vision",
    "nlp",
    "speech processing",
    "music tech",
    "film industry",
    "journalism",
    "politics",
    "governance",
    "public policy",
    "defense",
    "smart cities",
    "urban planning",
    "waste management",
    "water management",
    "renewable energy",
    "human resources",
    "recruitment",
    "education tech",
    "edtech analytics",
    "adtech",
    "fintech",
    "legal tech",
    "insurtech",
    "medtech",
    "agritech",
    "proptech",
    "retail analytics",
    "customer analytics",
    "behavioral science",
    "psychology",
    "linguistics",
    "ethics in ai",
    "assistive technology",
    "accessibility tech",
    "telemedicine",
    "quantitative finance",
    "civic tech",
)

# Map catalog / loose tokens → ontology term (first match in infer wins via longest phrase).
DOMAIN_ALIASES: Dict[str, str] = {
    "health": "healthcare",
    "clinical": "healthcare",
    "patient": "healthcare",
    "medical": "medtech",
    "artificial intelligence": "nlp",
    # Do NOT map ML / data science to customer analytics — that hijacks sector choice (e.g. climate).
    "computer vision": "computer vision",
    "natural language": "nlp",
    "justice": "law",
    "crime": "public policy",
    "women safety": "defense",
    "edtech": "education tech",
    "precision agriculture": "agriculture",
    "web development": "ecommerce",
    "mobile development": "ecommerce",
    "cloud computing": "telecommunications",
}


def _project_blob(project: Dict) -> str:
    parts: List[str] = [
        str(project.get("title", "")),
        str(project.get("description", "")),
        str(project.get("summary", "")),
        str(project.get("full_text", "")),
        str(project.get("sector", "")),
    ]
    dom = project.get("domain", [])
    if isinstance(dom, list):
        parts.extend(str(x) for x in dom)
    else:
        parts.append(str(dom))
    return " ".join(parts).lower()


def user_profile_hints(user: ProcessedInput) -> List[str]:
    """Sector first so industry context wins over catalog text and technical labels."""
    hints: List[str] = []
    sc = (getattr(user, "sector_context", None) or "").strip()
    if sc:
        hints.append(sc)
    ins = (getattr(user, "interests", None) or "").strip()
    if ins:
        hints.append(ins)
    hints.extend(user.domain_preference)
    return hints


def _ontology_from_intent_blob(blob: str) -> str | None:
    """Map free-text sector + interest strings to ontology before catalog text (Flask form has no sector field)."""
    s = (blob or "").lower().strip()
    if not s:
        return None
    if any(x in s for x in ("climate", "weather", "emission", "carbon", "decarbon", "global warming")):
        return "climate"
    if any(
        x in s
        for x in (
            "environment",
            "sustainability",
            "wildlife",
            "biodiversity",
            "pollution",
            "conservation",
            "renewable",
            "clean energy",
            "circular economy",
        )
    ):
        return "environment"
    if any(
        x in s
        for x in (
            "health",
            "healthcare",
            "medical",
            "clinical",
            "hospital",
            "patient",
            "pharma",
            "biotech",
            "life science",
            "life sciences",
        )
    ):
        return "healthcare"
    if any(x in s for x in ("finance", "banking", "insurance", "fintech", "trading", "credit")):
        return "finance"
    # Avoid matching "learning" inside "machine learning" / "deep learning"
    if any(x in s for x in ("education", "university", "school", "edtech", "curriculum", "classroom", "coursework")):
        return "education"
    if " research " in f" {s} " or s.startswith("research ") or s.endswith(" research"):
        return "education"
    if any(x in s for x in ("agriculture", "food system", "farm", "crop", "agritech")):
        return "agriculture"
    if any(x in s for x in ("energy", "utility", "utilities", "power grid")):
        return "energy"
    if any(x in s for x in ("transport", "mobility", "logistics", "automotive", "aerospace")):
        return "transportation"
    if any(x in s for x in ("retail", "e-commerce", "ecommerce", "commerce", "marketing", "customer")):
        return "retail analytics"
    if any(x in s for x in ("government", "public sector", "civic", "policy", "defense")):
        return "public policy"
    if any(x in s for x in ("legal", "compliance", "law ")):
        return "law"
    if any(x in s for x in ("real estate", "construction", "urban", "proptech")):
        return "real estate"
    if any(x in s for x in ("nonprofit", "social impact", "ngo")):
        return "civic tech"
    return None


def _stated_ontology_from_user(user: ProcessedInput) -> str | None:
    parts = [
        (getattr(user, "sector_context", None) or "").strip(),
        (getattr(user, "interests", None) or "").strip(),
    ]
    return _ontology_from_intent_blob(" ".join(p for p in parts if p))


def infer_ontology_domain(project: Dict, user: ProcessedInput) -> str:
    """Pick the single best ontology label: user sector → user hints → catalog text."""
    stated = _stated_ontology_from_user(user)
    if stated:
        return stated

    text = _project_blob(project)
    for ud in user_profile_hints(user):
        u = ud.strip().lower()
        if not u:
            continue
        for term in sorted(DOMAIN_ONTOLOGY, key=len, reverse=True):
            if term == u or term in u or u in term:
                return term
        if u in DOMAIN_ALIASES:
            return DOMAIN_ALIASES[u]

    best = ""
    for term in sorted(DOMAIN_ONTOLOGY, key=len, reverse=True):
        if term in text:
            best = term
            break
    if best:
        return best

    for alias, target in DOMAIN_ALIASES.items():
        if alias in text:
            return target

    return "education"


def ontology_to_cluster(ontology_domain: str) -> str:
    d = ontology_domain.lower()
    if d in {"healthcare", "mental health", "nutrition", "fitness", "medtech"}:
        return "health"
    if d in {"finance", "banking", "insurance", "fintech", "insurtech", "cryptocurrency"}:
        return "finance"
    if d in {"nlp", "linguistics", "speech processing", "journalism", "social media"}:
        return "nlp"
    if d in {"computer vision", "augmented reality", "virtual reality", "film industry"}:
        return "vision"
    if d in {"iot", "robotics", "automotive", "aerospace", "manufacturing", "smart cities", "supply chain"}:
        return "iot_industrial"
    if d in {"cybersecurity", "defense", "blockchain"}:
        return "security"
    if d in {"climate", "environment", "wildlife", "renewable energy", "water management", "waste management", "geology"}:
        return "environment"
    if d in {"education", "education tech", "edtech analytics"}:
        return "education"
    if d in {"gaming", "music tech", "sports"}:
        return "creative_signal"
    if d in {"law", "legal tech", "governance", "politics", "public policy"}:
        return "policy_law"
    if d in {"agriculture", "agritech", "food industry"}:
        return "agriculture"
    if d in {"fashion", "retail analytics", "ecommerce", "customer analytics", "marketing", "adtech"}:
        return "commerce"
    if d in {"real estate", "proptech", "urban planning", "transportation", "tourism", "hospitality"}:
        return "built_world"
    if d in {"human resources", "recruitment", "behavioral science", "psychology"}:
        return "people_analytics"
    if d in {"biotechnology", "pharmaceuticals", "astronomy", "space tech", "energy"}:
        return "stem"
    if d in {"ethics in ai", "assistive technology", "accessibility tech"}:
        return "responsible_ai"
    return "general"
