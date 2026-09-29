"""Lightweight validation for seed opportunity data."""
from __future__ import annotations
import json
from datetime import date
from pathlib import Path
from typing import Any
from backend.eligibility import PROFICIENCY_LEVELS

ROOT_FIELDS = {"id": str, "title": str, "organization": str, "opportunity_type": str, "description": str, "location": str, "remote": bool, "deadline": (str, type(None)), "source_url": (str, type(None)), "eligibility": dict, "matching": dict}
ELIGIBILITY_FIELDS = {"degree_levels": list, "accepted_majors": list, "nationality_requirements": list, "minimum_gpa": (int, float, type(None)), "language_requirements": dict}
MATCHING_FIELDS = {name: list for name in ("required_skills", "preferred_skills", "fields", "keywords")}

def _check_fields(value: dict[str, Any], fields: dict[str, Any], path: str, errors: list[str]) -> None:
    for name in sorted(fields.keys() - value.keys()): errors.append(f"{path}: missing field '{name}'")
    for name in sorted(value.keys() - fields.keys()): errors.append(f"{path}: unexpected field '{name}'")
    for name, expected in fields.items():
        if name in value and not isinstance(value[name], expected): errors.append(f"{path}.{name}: wrong type")

def validate_opportunities(opportunities: Any) -> list[str]:
    """Return structural errors; an empty list means valid."""
    if not isinstance(opportunities, list): return ["root: expected an array"]
    errors: list[str] = []; ids: set[str] = set()
    for index, opportunity in enumerate(opportunities):
        path = f"root[{index}]"
        if not isinstance(opportunity, dict): errors.append(f"{path}: expected an object"); continue
        _check_fields(opportunity, ROOT_FIELDS, path, errors)
        record_id = opportunity.get("id")
        if isinstance(record_id, str):
            if not record_id: errors.append(f"{path}.id: must not be empty")
            if record_id in ids: errors.append(f"{path}.id: duplicate '{record_id}'")
            ids.add(record_id)
        for name in ("title", "organization", "opportunity_type", "location"):
            if isinstance(opportunity.get(name), str) and not opportunity[name].strip(): errors.append(f"{path}.{name}: must not be empty")
        if isinstance(opportunity.get("deadline"), str):
            try: date.fromisoformat(opportunity["deadline"])
            except ValueError: errors.append(f"{path}.deadline: expected YYYY-MM-DD")
        eligibility = opportunity.get("eligibility")
        if isinstance(eligibility, dict):
            _check_fields(eligibility, ELIGIBILITY_FIELDS, f"{path}.eligibility", errors)
            gpa = eligibility.get("minimum_gpa")
            if isinstance(gpa, (int, float)) and not 0 <= gpa <= 4: errors.append(f"{path}.eligibility.minimum_gpa: expected 0 to 4")
            for field in ("degree_levels", "accepted_majors", "nationality_requirements"):
                if isinstance(eligibility.get(field), list) and not all(isinstance(x, str) for x in eligibility[field]): errors.append(f"{path}.eligibility.{field}: items must be strings")
            if isinstance(eligibility.get("language_requirements"), dict):
                for language, level in eligibility["language_requirements"].items():
                    if not isinstance(language, str) or not isinstance(level, str) or level.casefold() not in PROFICIENCY_LEVELS: errors.append(f"{path}.eligibility.language_requirements: invalid level for '{language}'")
        matching = opportunity.get("matching")
        if isinstance(matching, dict):
            _check_fields(matching, MATCHING_FIELDS, f"{path}.matching", errors)
            for field in MATCHING_FIELDS:
                if isinstance(matching.get(field), list) and not all(isinstance(x, str) for x in matching[field]): errors.append(f"{path}.matching.{field}: items must be strings")
    return errors

def main() -> None:
    path = Path(__file__).resolve().parents[1] / "data/opportunities.json"
    try: opportunities = json.loads(path.read_text())
    except json.JSONDecodeError as exc: raise SystemExit(f"Invalid JSON: {exc}") from exc
    errors = validate_opportunities(opportunities)
    if errors: raise SystemExit("Validation failed:\n- " + "\n- ".join(errors))
    print(f"Valid: {len(opportunities)} opportunity records")

if __name__ == "__main__": main()
