"""Resolve a concrete dataset name + URL for API output (no placeholder labels)."""

from __future__ import annotations

import re
from typing import Dict, List, Tuple
from urllib.parse import quote_plus

_KAGGLE_DATASET = re.compile(r"kaggle\.com/(?:datasets/|c/|competitions/)", re.I)
_SYNTHETIC = re.compile(
    r"(?i)\b(complaint|incidents?|operational logs|metrics time series|demand forecasting|"
    r"feedback text|cctv|surveillance|fraud|transaction|anomalies?|seasonality)\w*\s+dataset\s*$"
)


def _kaggle_search(q: str) -> str:
    q = " ".join((q or "").split())
    return f"https://www.kaggle.com/search?q={quote_plus(q)}" if q else ""


_STARTERS: Dict[str, List[Tuple[str, str]]] = {
    "health": [
        ("Pima Indians Diabetes Database", "https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database"),
        ("Heart Disease Prediction", "https://www.kaggle.com/datasets/johnsmith88/heart-disease-dataset"),
    ],
    "finance": [
        ("Credit Card Fraud Detection", "https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud"),
        ("IEEE-CIS Fraud Detection", "https://www.kaggle.com/c/ieee-fraud-detection"),
    ],
    "nlp": [
        ("IMDB Dataset of 50K Movie Reviews", "https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews"),
        ("SMS Spam Collection Dataset", "https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset"),
    ],
    "vision": [
        ("Intel Image Classification", "https://www.kaggle.com/datasets/puneet6060/intel-image-classification"),
        ("Dogs vs Cats Redux", "https://www.kaggle.com/c/dogs-vs-cats-redux-kernels-edition"),
    ],
    "iot_industrial": [
        ("Machine Predictive Maintenance Classification", "https://www.kaggle.com/datasets/shivamb/machine-predictive-maintenance-classification"),
        ("Quality Prediction in Mining Process", "https://www.kaggle.com/datasets/edumagalhaes/quality-prediction-in-a-mining-process"),
    ],
    "security": [
        ("NSL-KDD Intrusion Detection", "https://www.kaggle.com/datasets/programmer3/nsl-kdd-intrusion-detection-dataset"),
        ("Network Intrusion UNR-IDD", "https://www.kaggle.com/datasets/mostafanofal/network-intrusion-detection-dataset-unr-idd"),
    ],
    "agriculture": [
        ("Crop Yield Prediction Dataset", "https://www.kaggle.com/datasets/patelris/crop-yield-prediction-dataset"),
        (
            "Crop Disease Image Classification",
            "https://www.kaggle.com/datasets/killa92/crop-disease-image-classification-dataset",
        ),
    ],
    "environment": [
        ("Wildfire Satellite Data", "https://www.kaggle.com/datasets/washingtongold/wildfire-satellite-data"),
        ("Global Country CO2 Emissions", "https://www.kaggle.com/datasets/ishanjaffer/global-countrys-co2-emissions"),
        ("Weather History (visual crossing style starter)", "https://www.kaggle.com/datasets/muthuj7/weather-dataset"),
    ],
    "commerce": [
        ("Brazilian E-Commerce Olist", "https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce"),
        ("Online Retail II (UCI)", "https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci"),
    ],
    "default": [
        ("Titanic", "https://www.kaggle.com/c/titanic"),
        ("House Prices: Advanced Regression", "https://www.kaggle.com/c/house-prices-advanced-regression-techniques"),
        ("California Housing Prices", "https://www.kaggle.com/datasets/camnugent/california-housing-prices"),
    ],
}


def _pool_key(ontology_cluster: str) -> str:
    """Map fine-grained routing cluster → curated URL pool."""
    m = {
        "health": "health",
        "finance": "finance",
        "nlp": "nlp",
        "vision": "vision",
        "iot_industrial": "iot_industrial",
        "security": "security",
        "agriculture": "agriculture",
        "commerce": "commerce",
        "education": "default",
        "environment": "environment",
        "creative_signal": "nlp",
        "policy_law": "default",
        "people_analytics": "default",
        "built_world": "default",
        "stem": "health",
        "responsible_ai": "default",
        "general": "default",
    }
    return m.get(ontology_cluster, "default")


def _is_concrete(url: str) -> bool:
    return bool(url and _KAGGLE_DATASET.search(url))


def _synthetic_name(name: str) -> bool:
    n = (name or "").strip().lower()
    if not n or "source required" in n:
        return True
    return bool(_SYNTHETIC.search(n))


def resolve_dataset(project: Dict, ontology_cluster: str) -> Tuple[str, str]:
    raw_name = str(project.get("dataset_name", "")).strip()
    link = str(project.get("dataset_link", "")).strip()
    display = raw_name or str(project.get("title", "Dataset"))

    opts = project.get("dataset_options")
    if isinstance(opts, list):
        for o in opts:
            if isinstance(o, dict):
                ol = str(o.get("link", "")).strip()
                on = str(o.get("name", "")).strip()
                if _is_concrete(ol) and not _synthetic_name(on or display):
                    return (on or display), ol

    if _is_concrete(link) and not _synthetic_name(display):
        return display, link

    if _synthetic_name(display) or "kaggle.com/search" in link or not link:
        pool = _STARTERS[_pool_key(ontology_cluster)]
        seed = f"{project.get('title','')}|{project.get('sector','')}|{raw_name}"
        idx = sum(ord(c) for c in seed) % len(pool)
        return pool[idx]

    if not link:
        return display, _kaggle_search(display)

    return display, link
