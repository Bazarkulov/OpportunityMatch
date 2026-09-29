"""Adapter for Lever's documented public Postings API."""
from __future__ import annotations
from datetime import datetime, timezone
from backend.collectors.base import BaseCollector, CollectorError
from backend.normalization import RawOpportunity, is_student_opportunity

class LeverCollector(BaseCollector):
    def __init__(self, site: str, timeout: float = 20.0):
        super().__init__(timeout); self.site = site; self.source_name = f"lever:{site}"
    def collect(self) -> list[RawOpportunity]:
        data = self.get_json(f"https://api.lever.co/v0/postings/{self.site}?mode=json")
        if not isinstance(data, list): raise CollectorError(f"{self.source_name}: unexpected response")
        results = []
        for job in data:
            lists = "\n".join(f"<h3>{item.get('text','')}</h3>{item.get('content','')}" for item in job.get("lists", []))
            content = f"{job.get('description','')}\n{job.get('additional','')}\n{lists}"
            if not is_student_opportunity(job.get("text", ""), job.get("descriptionPlain", "") + content): continue
            created = datetime.fromtimestamp(job["createdAt"] / 1000, timezone.utc) if job.get("createdAt") else None
            categories = job.get("categories") or {}
            location = categories.get("location") or job.get("workplaceType")
            results.append(RawOpportunity(str(job["id"]), job["text"], self.site.replace("-", " ").title(), self.source_name, job.get("hostedUrl") or job.get("applyUrl"), location, content, created, job))
        return results
