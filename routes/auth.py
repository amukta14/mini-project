from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

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
    return redirect(url_for("dashboard"))


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
    return redirect(url_for("dashboard"))


@auth_bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))
