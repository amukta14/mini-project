from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, abort, redirect, render_template, send_from_directory, session, url_for

from core.db import db
from models import StudentProfile
from routes.auth import auth_bp
from routes.recommend import recommend_bp
from services.auth_service import login_required


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(app.root_path, 'app.db')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    app.register_blueprint(auth_bp)
    app.register_blueprint(recommend_bp)

    # Serve React (Vite build) as the main UI.
    dist_dir = Path(app.root_path) / "frontend" / "new_ui" / "dist"
    assets_dir = dist_dir / "assets"

    @app.get("/assets/<path:filename>")
    def spa_assets(filename: str):
        if not assets_dir.exists():
            abort(404)
        return send_from_directory(assets_dir, filename)

    @app.get("/")
    def landing() -> str:
        if dist_dir.exists():
            return send_from_directory(dist_dir, "index.html")
        if session.get("student_id"):
            return redirect(url_for("questionnaire"))
        return render_template("landing.html")

    @app.get("/questionnaire")
    @login_required
    def questionnaire() -> str:
        profile = StudentProfile.query.filter_by(student_id=session["student_id"]).first()
        return render_template("questionnaire.html", student_name=session.get("student_name", "Student"), profile=profile)

    @app.get("/dashboard")
    @login_required
    def dashboard() -> str:
        profile = StudentProfile.query.filter_by(student_id=session["student_id"]).first()
        return render_template("dashboard.html", student_name=session.get("student_name", "Student"), profile=profile)

    # SPA fallback: React Router handles client-side routes.
    @app.get("/<path:path>")
    def spa_fallback(path: str):
        if path.startswith("api") or path.startswith("recommend") or path.startswith("assets"):
            abort(404)
        if dist_dir.exists():
            return send_from_directory(dist_dir, "index.html")
        abort(404)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5050")), debug=True)
