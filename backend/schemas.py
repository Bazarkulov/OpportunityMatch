"""Validated API request and response contracts."""
from __future__ import annotations
from datetime import date, datetime
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, model_validator

class AuthRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)

class UserOut(BaseModel):
    id: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class ProfileBase(BaseModel):
    degree_level: str | None = None
    university: str | None = None
    major: str | None = None
    academic_year: str | None = None
    nationality: str | None = None
    gpa: float | None = Field(default=None, ge=0)
    gpa_scale: float | None = Field(default=None, gt=0)
    languages: dict[str, str] = Field(default_factory=dict)
    skills: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    preferred_opportunity_types: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    remote_preference: bool | None = None
    extra_data: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def valid_gpa(self):
        if self.gpa is not None and self.gpa_scale is None:
            raise ValueError("gpa_scale is required when gpa is provided")
        if self.gpa is not None and self.gpa_scale is not None and self.gpa > self.gpa_scale:
            raise ValueError("gpa cannot exceed gpa_scale")
        return self

class ProfileUpdate(ProfileBase):
    pass

class ProfileOut(ProfileBase):
    id: str
    user_id: str
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class OpportunityOut(BaseModel):
    id: str
    external_id: str
    title: str
    organization: str
    description: str
    opportunity_type: str | None
    source: str
    source_url: str
    location: str | None
    remote: bool | None
    deadline: date | None
    published_at: datetime | None
    discovered_at: datetime
    funding_status: str | None
    degree_requirements: list[str] | None
    major_requirements: list[str] | None
    nationality_restrictions: list[str] | None
    minimum_gpa: float | None
    gpa_scale: float | None
    language_requirements: dict[str, str] | None
    required_skills: list[str] | None
    preferred_skills: list[str] | None
    fields: list[str] | None
    keywords: list[str] | None
    collected_at: datetime
    last_verified_at: datetime
    active: bool
    saved: bool = False
    model_config = ConfigDict(from_attributes=True)

class EligibilityResult(BaseModel):
    status: Literal["eligible", "ineligible", "uncertain"]
    passed: list[str]
    failed: list[str]
    unknown: list[str]

class MatchComponent(BaseModel):
    name: str
    score: float
    weight: float
    explanation: str

class MatchResult(BaseModel):
    overall_score: float
    components: list[MatchComponent]
    matched_characteristics: list[str]
    missing_preferred_characteristics: list[str]
    explanation: str

class RecommendationOut(BaseModel):
    opportunity: OpportunityOut
    eligibility: EligibilityResult
    match: MatchResult

class CollectionResult(BaseModel):
    run_id: str
    status: str
    sources_succeeded: int
    sources_failed: int
    records_seen: int
    records_upserted: int
    errors: list[str]
