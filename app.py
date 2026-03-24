from __future__ import annotations

import os

from flask import Flask, redirect, render_template, session, url_for

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

    @app.get("/")
    def landing() -> str:
        if session.get("student_id"):
            return redirect(url_for("dashboard"))
        return render_template("landing.html")

    @app.get("/dashboard")
    @login_required
    def dashboard() -> str:
        profile = StudentProfile.query.filter_by(student_id=session["student_id"]).first()
        return render_template("dashboard.html", student_name=session.get("student_name", "Student"), profile=profile)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5050")), debug=True)
