"""Auditable deterministic normalization; absent requirements stay unknown."""
from __future__ import annotations
import hashlib
import html
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any
from bs4 import BeautifulSoup

@dataclass
class RawOpportunity:
    external_id: str
    title: str
    organization: str
    source: str
    source_url: str
    location: str | None
    content_html: str
    published_at: datetime | None = None
    metadata: dict[str, Any] | None = None

DEGREES = {
    "bachelor": "Bachelor's", "undergraduate": "Bachelor's", "master": "Master's",
    "graduate student": "Master's", "doctoral": "Doctoral", "phd": "Doctoral",
}
FIELDS = ["Computer Science", "Data Science", "Engineering", "Robotics", "Economics", "Finance", "Design", "Public Policy", "Environmental Science", "Biology", "Chemistry", "Physics", "Mathematics"]
SKILLS = ["Python", "JavaScript", "TypeScript", "React", "SQL", "C++", "Java", "Machine Learning", "Computer Vision", "ROS2", "Data Analysis", "Research", "Writing", "Figma", "Cloud Computing", "Git"]
STUDENT_TERMS = re.compile(r"\b(intern(ship)?|student|undergraduate|graduate|new grad(uate)?|fellow(ship)?|scholar(ship)?|research assistant|co-?op|trainee)\b", re.I)

def clean_html(value: str) -> str:
    soup = BeautifulSoup(html.unescape(value or ""), "html.parser")
    return "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())

def is_student_opportunity(title: str, text: str) -> bool:
    return bool(STUDENT_TERMS.search(f"{title}\n{text}"))

def _mentions(text: str, candidates: list[str]) -> list[str]:
    lower = text.casefold()
    return [value for value in candidates if re.search(rf"(?<!\w){re.escape(value.casefold())}(?!\w)", lower)]

def _degree_requirements(text: str) -> list[str] | None:
    lower = text.casefold()
    found = {canonical for phrase, canonical in DEGREES.items() if re.search(rf"\b{re.escape(phrase)}(?:'s)?\b", lower)}
    return sorted(found) or None

def _major_requirements(text: str) -> list[str] | None:
    requirement_lines = [line for line in text.splitlines() if re.search(r"\b(pursuing|degree in|major(?:ing)? in|students? in|enrolled in)\b", line, re.I)]
    found: list[str] = []
    for line in requirement_lines: found.extend(_mentions(line, FIELDS))
    return list(dict.fromkeys(found)) or None

def _required_skills(text: str) -> list[str] | None:
    requirement_lines = [line for line in text.splitlines() if re.search(r"\b(required|requirements?|proficien(?:t|cy)|experience (?:with|in)|knowledge of|familiar(?:ity)? with)\b", line, re.I)]
    found: list[str] = []
    for line in requirement_lines: found.extend(_mentions(line, SKILLS))
    return list(dict.fromkeys(found)) or None

def _minimum_gpa(text: str) -> tuple[float | None, float | None]:
    match = re.search(r"(?:minimum|min\.?|at least)\s+(?:cumulative\s+)?gpa(?:\s+of)?\s*[:≥>=-]?\s*(\d(?:\.\d+)?)\s*(?:/|out of\s*)?(4(?:\.0)?|5(?:\.0)?|10(?:\.0)?)?", text, re.I)
    if not match: return None, None
    value = float(match.group(1)); scale = float(match.group(2)) if match.group(2) else 4.0
    return (value, scale) if 0 <= value <= scale else (None, None)

def _deadline(text: str) -> date | None:
    for pattern in (r"(?:deadline|apply by|applications? close)\s*[:\-]?\s*(\d{4}-\d{2}-\d{2})", r"(?:deadline|apply by|applications? close)\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{4})"):
        match = re.search(pattern, text, re.I)
        if match:
            try:
                return datetime.strptime(match.group(1), "%Y-%m-%d" if "-" in match.group(1) else "%m/%d/%Y").date()
            except ValueError: pass
    return None

def _opportunity_type(title: str, text: str) -> str | None:
    value = f"{title} {text[:500]}".casefold()
    for phrase, canonical in (("research internship", "Research Internship"), ("intern", "Internship"), ("fellow", "Fellowship"), ("scholar", "Scholarship"), ("exchange", "Exchange Program"), ("research assistant", "Research"), ("co-op", "Co-op"), ("new grad", "Graduate Program")):
        if phrase in value: return canonical
    return None

def normalize(raw: RawOpportunity) -> dict[str, Any]:
    text = clean_html(raw.content_html)
    combined = f"{raw.title}\n{text}"
    minimum_gpa, gpa_scale = _minimum_gpa(combined)
    location = raw.location.strip() if raw.location else None
    remote = True if re.search(r"\bremote\b", location or "", re.I) else (False if location else None)
    fields = _mentions(combined, FIELDS) or None
    skills = _mentions(combined, SKILLS) or None
    funding = "Paid" if re.search(r"\b(paid|salary|compensation|stipend)\b", combined, re.I) else None
    fingerprint_text = f"{raw.organization}|{raw.title}|{location or ''}".casefold()
    now = datetime.now(timezone.utc)
    deadline = _deadline(combined)
    return {
        "external_id": raw.external_id, "fingerprint": hashlib.sha256(fingerprint_text.encode()).hexdigest(),
        "title": raw.title.strip(), "organization": raw.organization.strip(), "description": text,
        "opportunity_type": _opportunity_type(raw.title, text), "source": raw.source,
        "source_url": raw.source_url, "location": location, "remote": remote, "deadline": deadline,
        "published_at": raw.published_at, "funding_status": funding,
        "degree_requirements": _degree_requirements(combined), "major_requirements": _major_requirements(text),
        "nationality_restrictions": None, "minimum_gpa": minimum_gpa, "gpa_scale": gpa_scale,
        "language_requirements": None, "required_skills": _required_skills(text), "preferred_skills": None,
        "fields": fields, "keywords": skills, "raw_source_text": text,
        "collected_at": now, "last_verified_at": now,
        "active": deadline is None or deadline >= now.date(),
    }
