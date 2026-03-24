from __future__ import annotations

from typing import Dict, List

def filter_projects_by_domain(projects: List[Dict], selected_domains: List[str]) -> List[Dict]:
    """Return projects matching at least one selected domain."""
    if not selected_domains:
        return projects

    selected = set(selected_domains)
    filtered: List[Dict] = []
    for project in projects:
        project_domains = project.get("domain", [])
        if isinstance(project_domains, str):
            project_domains = [project_domains]
        if selected.intersection(set(project_domains)):
            filtered.append(project)
    return filtered
