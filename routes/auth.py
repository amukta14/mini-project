from __future__ import annotations

from http import HTTPStatus

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from models import Student
from services.auth_service import create_student, verify_password


auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/signup")
def signup() -> str:
    return render_template("signup.html")


@auth_bp.post("/signup")
def signup_post():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not name or not email or len(password) < 8:
        flash("Provide name, valid email, and password with at least 8 characters.", "error")
        return redirect(url_for("auth.signup"))
    try:
        student = create_student(name=name, email=email, password=password)
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("auth.signup"))

    session["student_id"] = student.id
    session["student_name"] = student.name
    return redirect(url_for("questionnaire"))


@auth_bp.get("/login")
def login() -> str:
    return render_template("login.html")


@auth_bp.post("/login")
def login_post():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    student = Student.query.filter_by(email=email).first()
    if not student or not verify_password(student.password_hash, password):
        flash("Invalid email or password.", "error")
        return redirect(url_for("auth.login"))

    session["student_id"] = student.id
    session["student_name"] = student.name
    return redirect(url_for("questionnaire"))


@auth_bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


# JSON API for React SPA
@auth_bp.get("/api/me")
def api_me():
    if not session.get("student_id"):
        return jsonify({"authenticated": False}), HTTPStatus.OK
    return (
        jsonify(
            {
                "authenticated": True,
                "student_id": session.get("student_id"),
                "student_name": session.get("student_name"),
            }
        ),
        HTTPStatus.OK,
    )


@auth_bp.post("/api/login")
def api_login():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))

    student = Student.query.filter_by(email=email).first()
    if not student or not verify_password(student.password_hash, password):
        return jsonify({"error": "Invalid email or password."}), HTTPStatus.UNAUTHORIZED

    session["student_id"] = student.id
    session["student_name"] = student.name
    return jsonify({"ok": True}), HTTPStatus.OK


@auth_bp.post("/api/register")
def api_register():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))

    if not name or not email or len(password) < 8:
        return (
            jsonify({"error": "Provide name, valid email, and password with at least 8 characters."}),
            HTTPStatus.BAD_REQUEST,
        )

    try:
        student = create_student(name=name, email=email, password=password)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.BAD_REQUEST

    session["student_id"] = student.id
    session["student_name"] = student.name
    return jsonify({"ok": True}), HTTPStatus.OK


@auth_bp.post("/api/logout")
def api_logout():
    session.clear()
    return jsonify({"ok": True}), HTTPStatus.OK
