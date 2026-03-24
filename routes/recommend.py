from __future__ import annotations

import json
from http import HTTPStatus
from typing import Any, Dict

import numpy as np
from flask import Blueprint, jsonify, request, session

from core.db import db
from models import StudentProfile

from services.data_service import DataService
from services.domain_service import filter_projects_by_domain
from services.embedding_service import create_query_embedding
from services.filtering_service import apply_feasibility_filters
from services.preprocessing_service import process_user_input
from services.ranking_service import rank_projects


recommend_bp = Blueprint("recommend", __name__)
data_service = DataService()


@recommend_bp.post("/recommend")
def recommend_projects() -> tuple[Any, int]:
    try:
        if "student_id" not in session:
            return jsonify({"error": "Authentication required."}), HTTPStatus.UNAUTHORIZED

        payload: Dict[str, Any] = request.get_json(silent=True) or {}
        user_input = process_user_input(payload)

        profile = StudentProfile.query.filter_by(student_id=session["student_id"]).first()
        if profile:
            profile.skills = json.dumps(user_input.skills)
            profile.interests = user_input.interests
            profile.experience_level = user_input.experience_level
            profile.time_available = user_input.time_available
            profile.domain_preference = json.dumps(user_input.domain_preference)
            db.session.commit()

        projects, project_embeddings = data_service.get_projects_with_embeddings()
        domain_filtered = filter_projects_by_domain(projects, user_input.domain_preference)
        filtered_projects = domain_filtered if domain_filtered else projects
        filtered_projects = apply_feasibility_filters(filtered_projects, user_input)

        if not filtered_projects:
            return jsonify({"recommendations": [], "message": "No projects matched your selected filters."}), HTTPStatus.OK

        index_map = {id(project): idx for idx, project in enumerate(projects)}
        filtered_embeddings = np.vstack([project_embeddings[index_map[id(project)]] for project in filtered_projects])

        query_embedding = create_query_embedding(user_input.semantic_query)
        recommendations = rank_projects(user_input, query_embedding, filtered_projects, filtered_embeddings)

        return jsonify({"recommendations": recommendations}), HTTPStatus.OK
    except ValueError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.BAD_REQUEST
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.INTERNAL_SERVER_ERROR
    except Exception:
        return jsonify({"error": "Unexpected server error while generating recommendations."}), HTTPStatus.INTERNAL_SERVER_ERROR
