"""Relational persistence models, portable across SQLite and PostgreSQL."""
from __future__ import annotations
from datetime import date, datetime, timezone
from uuid import uuid4
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    profile: Mapped["StudentProfile | None"] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False)

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    degree_level: Mapped[str | None] = mapped_column(String(80), nullable=True)
    university: Mapped[str | None] = mapped_column(String(250), nullable=True)
    major: Mapped[str | None] = mapped_column(String(160), nullable=True)
    academic_year: Mapped[str | None] = mapped_column(String(80), nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(100), nullable=True)
    gpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    gpa_scale: Mapped[float | None] = mapped_column(Float, nullable=True)
    languages: Mapped[dict] = mapped_column(JSON, default=dict)
    skills: Mapped[list] = mapped_column(JSON, default=list)
    interests: Mapped[list] = mapped_column(JSON, default=list)
    preferred_opportunity_types: Mapped[list] = mapped_column(JSON, default=list)
    preferred_locations: Mapped[list] = mapped_column(JSON, default=list)
    remote_preference: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    user: Mapped[User] = relationship(back_populates="profile")

class Opportunity(Base):
    __tablename__ = "opportunities"
    __table_args__ = (UniqueConstraint("source", "external_id", name="uq_opportunity_source_external"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    external_id: Mapped[str] = mapped_column(String(250))
    fingerprint: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(500))
    organization: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text)
    opportunity_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source: Mapped[str] = mapped_column(String(120), index=True)
    source_url: Mapped[str] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(300), nullable=True)
    remote: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    funding_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    degree_requirements: Mapped[list | None] = mapped_column(JSON, nullable=True)
    major_requirements: Mapped[list | None] = mapped_column(JSON, nullable=True)
    nationality_restrictions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    minimum_gpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    gpa_scale: Mapped[float | None] = mapped_column(Float, nullable=True)
    language_requirements: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    required_skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    preferred_skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    fields: Mapped[list | None] = mapped_column(JSON, nullable=True)
    keywords: Mapped[list | None] = mapped_column(JSON, nullable=True)
    raw_source_text: Mapped[str] = mapped_column(Text)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

class SavedOpportunity(Base):
    __tablename__ = "saved_opportunities"
    __table_args__ = (UniqueConstraint("user_id", "opportunity_id", name="uq_saved_user_opportunity"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    opportunity: Mapped[Opportunity] = relationship()

class CollectionRun(Base):
    __tablename__ = "collection_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="running")
    sources_succeeded: Mapped[int] = mapped_column(default=0)
    sources_failed: Mapped[int] = mapped_column(default=0)
    records_seen: Mapped[int] = mapped_column(default=0)
    records_upserted: Mapped[int] = mapped_column(default=0)
    errors: Mapped[list] = mapped_column(JSON, default=list)
