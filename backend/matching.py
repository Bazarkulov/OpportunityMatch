"""Configurable hybrid relevance scoring, separate from eligibility."""
from __future__ import annotations
import hashlib, math, re
from collections import Counter
from typing import Any, Protocol

DEFAULT_WEIGHTS = {"skill_overlap": .20, "skill_semantic": .15, "major_field": .20, "interest_topic": .20, "opportunity_type": .10, "location": .10, "remote": .05}
SYNONYMS = {"ai": "artificial intelligence", "ml": "machine learning", "cv": "computer vision", "cs": "computer science", "software engineering": "computer science", "data analytics": "data analysis", "ux": "user experience"}
def _get(value: Any, name: str, default=None): return value.get(name, default) if isinstance(value, dict) else getattr(value, name, default)
def _norm(value: str) -> str: return re.sub(r"\s+", " ", value.strip().casefold())
def _values(value: Any, name: str) -> list[str]: return list(_get(value, name) or [])

class SimilarityProvider(Protocol):
    def similarity(self, left: list[str], right: list[str]) -> float: ...

class HashedSemanticSimilarity:
    """Offline text vectors with synonym expansion and cosine similarity."""
    dimensions = 512
    def _vector(self, values: list[str]) -> Counter[int]:
        vector: Counter[int] = Counter()
        for value in values:
            normalized = SYNONYMS.get(_norm(value), _norm(value)); tokens = re.findall(r"[a-z0-9+#]+", normalized)
            for feature in tokens + [f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens)-1)]: vector[int(hashlib.sha256(feature.encode()).hexdigest()[:8], 16) % self.dimensions] += 1
        return vector
    def similarity(self, left: list[str], right: list[str]) -> float:
        if not left or not right: return 0.0
        a, b = self._vector(left), self._vector(right); denominator = math.sqrt(sum(v*v for v in a.values()) * sum(v*v for v in b.values()))
        return min(1.0, sum(value * b.get(key, 0) for key, value in a.items()) / denominator) if denominator else 0.0

def score_relevance(student: Any, opportunity: Any, similarity: SimilarityProvider | None = None, weights: dict[str, float] | None = None) -> dict[str, Any]:
    similarity, weights = similarity or HashedSemanticSimilarity(), weights or DEFAULT_WEIGHTS
    if not math.isclose(sum(weights.values()), 1.0): raise ValueError("Matching weights must sum to 1.0")
    skills, required, preferred = _values(student, "skills"), _values(opportunity, "required_skills"), _values(opportunity, "preferred_skills")
    target_skills = required + preferred; student_set = {_norm(x) for x in skills}; exact = [x for x in target_skills if _norm(x) in student_set]
    exact_ratio = len({_norm(x) for x in exact}) / len({_norm(x) for x in target_skills}) if target_skills else 0.0
    fields = _values(opportunity, "fields") or _values(opportunity, "major_requirements"); major = _get(student, "major") or ""
    major_similarity = similarity.similarity([major], fields); interests = _values(student, "interests"); topics = fields + _values(opportunity, "keywords")
    interest_similarity, semantic_skills = similarity.similarity(interests, topics), similarity.similarity(skills, target_skills)
    preferred_types = {_norm(x) for x in _values(student, "preferred_opportunity_types")}; opportunity_type = _get(opportunity, "opportunity_type")
    type_score = 1.0 if opportunity_type and _norm(opportunity_type) in preferred_types else 0.0
    location = _norm(_get(opportunity, "location") or ""); preferences = [_norm(x) for x in _values(student, "preferred_locations")]
    location_score = 1.0 if location and any(p in location or location in p for p in preferences if p != "remote") else 0.0
    remote, remote_preference = _get(opportunity, "remote"), _get(student, "remote_preference")
    remote_score = 1.0 if remote_preference is None or remote is None else float(remote == remote_preference or (remote_preference and remote))
    raw = {"skill_overlap": exact_ratio, "skill_semantic": semantic_skills, "major_field": major_similarity, "interest_topic": interest_similarity, "opportunity_type": type_score, "location": location_score, "remote": remote_score}
    explanations = {"skill_overlap": f"Exact skill matches: {exact or ['none']}.", "skill_semantic": "Semantic similarity between profile skills and published opportunity skills.", "major_field": f"Similarity between major '{major or 'not provided'}' and fields {fields or ['unknown']}.", "interest_topic": f"Similarity between interests and topics {topics or ['unknown']}.", "opportunity_type": f"Type '{opportunity_type or 'unknown'}' {'matches' if type_score else 'does not match'} preferences.", "location": f"Location '{_get(opportunity, 'location') or 'unknown'}' {'matches' if location_score else 'does not match'} preferences.", "remote": "Remote status aligns with the preference or one side is unknown." if remote_score else "Remote status conflicts with the preference."}
    components = [{"name": name, "score": round(raw[name] * 100, 1), "weight": weight, "explanation": explanations[name]} for name, weight in weights.items()]
    overall = round(sum(raw[name] * weight for name, weight in weights.items()) * 100, 1); missing = [x for x in preferred if _norm(x) not in student_set]
    matched = list(dict.fromkeys(exact + ([major] if major_similarity >= .6 and major else []) + [x for x in interests if similarity.similarity([x], topics) >= .6]))
    return {"overall_score": overall, "components": components, "matched_characteristics": matched, "missing_preferred_characteristics": missing, "explanation": f"{overall:.0f}% match based on weighted skills, field, interests, type, location, and remote preference."}
