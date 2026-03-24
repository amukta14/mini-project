from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import redirect, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from core.db import db
from models import Student, StudentProfile


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)


def create_student(name: str, email: str, password: str) -> Student:
    existing = Student.query.filter_by(email=email).first()
    if existing:
        raise ValueError("An account with this email already exists.")

    student = Student(name=name, email=email, password_hash=hash_password(password))
    db.session.add(student)
    db.session.flush()
    db.session.add(StudentProfile(student_id=student.id))
    db.session.commit()
    return student


def login_required(view_func: Callable):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "student_id" not in session:
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapper
