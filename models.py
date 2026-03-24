from __future__ import annotations

from datetime import datetime

from core.db import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    profile = db.relationship("StudentProfile", back_populates="student", uselist=False, cascade="all, delete-orphan")


class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), unique=True, nullable=False)
    skills = db.Column(db.Text, nullable=False, default="[]")
    interests = db.Column(db.Text, nullable=False, default="")
    experience_level = db.Column(db.String(32), nullable=False, default="")
    time_available = db.Column(db.String(32), nullable=False, default="")
    domain_preference = db.Column(db.Text, nullable=False, default="[]")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    student = db.relationship("Student", back_populates="profile")
