"""Three-state deterministic eligibility, independent of relevance scoring."""
from __future__ import annotations
from typing import Any

PROFICIENCY_LEVELS = {"none required": 0, "basic": 1, "conversational": 2, "professional fluency": 3, "native": 4}
def _get(value: Any, name: str): return value.get(name) if isinstance(value, dict) else getattr(value, name, None)
def _norm(value: str) -> str: return value.strip().casefold()

def evaluate_eligibility(student: Any, opportunity: Any) -> dict[str, Any]:
    passed: list[str] = []; failed: list[str] = []; unknown: list[str] = []
    def record(condition: bool | None, success: str, failure: str, missing: str) -> None:
        (passed if condition is True else failed if condition is False else unknown).append(success if condition is True else failure if condition is False else missing)
    degree, degrees = _get(student, "degree_level"), _get(opportunity, "degree_requirements")
    if degrees is None: record(None, "", "", "Degree requirements were not published.")
    elif not degrees or any(_norm(x) == "any" for x in degrees): record(True, "No degree restriction was published.", "", "")
    elif not degree: record(None, "", "", "Student degree level is missing.")
    else: record(_norm(degree) in {_norm(x) for x in degrees}, f"Degree level {degree} is accepted.", f"Degree level {degree} is not among {degrees}.", "")
    major, majors = _get(student, "major"), _get(opportunity, "major_requirements")
    if majors is None: record(None, "", "", "Major or field requirements were not published.")
    elif not majors or any(_norm(x) == "any" for x in majors): record(True, "No major restriction was published.", "", "")
    elif not major: record(None, "", "", "Student major is missing.")
    else: record(_norm(major) in {_norm(x) for x in majors}, f"Major {major} is accepted.", f"Major {major} is not among {majors}.", "")
    nationality, nationalities = _get(student, "nationality"), _get(opportunity, "nationality_restrictions")
    if nationalities is None: record(None, "", "", "Nationality eligibility was not published.")
    elif not nationalities or any(_norm(x) == "any" for x in nationalities): record(True, "No nationality restriction was published.", "", "")
    elif not nationality: record(None, "", "", "Student nationality is missing.")
    else: record(_norm(nationality) in {_norm(x) for x in nationalities}, f"Nationality {nationality} is accepted.", f"Nationality {nationality} is not among {nationalities}.", "")
    minimum, required_scale = _get(opportunity, "minimum_gpa"), _get(opportunity, "gpa_scale")
    student_gpa, student_scale = _get(student, "gpa"), _get(student, "gpa_scale")
    if minimum is None: record(None, "", "", "Minimum GPA was not published.")
    elif student_gpa is None or student_scale is None: record(None, "", "", "Student GPA or GPA scale is missing.")
    else:
        normalized, threshold = student_gpa / student_scale, minimum / (required_scale or 4.0)
        record(normalized >= threshold, f"Normalized GPA {normalized:.1%} meets the {threshold:.1%} minimum.", f"Normalized GPA {normalized:.1%} is below the {threshold:.1%} minimum.", "")
    requirements, languages = _get(opportunity, "language_requirements"), _get(student, "languages") or {}
    if requirements is None: record(None, "", "", "Language requirements were not published.")
    elif not requirements: record(True, "No language restriction was published.", "", "")
    else:
        student_languages = {_norm(k): v for k, v in languages.items()}
        for language, required in requirements.items():
            actual, needed = student_languages.get(_norm(language)), PROFICIENCY_LEVELS.get(_norm(required))
            if needed is None: record(None, "", "", f"Published {language} level '{required}' is not recognized.")
            elif needed == 0: record(True, f"{language} is not required.", "", "")
            elif actual is None: record(False, "", f"Required {language} ({required}) is not listed in the profile.", "")
            else:
                actual_rank = PROFICIENCY_LEVELS.get(_norm(actual))
                record(None if actual_rank is None else actual_rank >= needed, f"{language} level {actual} meets {required}.", f"{language} level {actual} is below {required}.", f"Student {language} level '{actual}' is not recognized.")
    return {"status": "ineligible" if failed else "uncertain" if unknown else "eligible", "passed": passed, "failed": failed, "unknown": unknown}

def check_eligibility(student: Any, opportunity: Any) -> dict[str, Any]: return evaluate_eligibility(student, opportunity)
