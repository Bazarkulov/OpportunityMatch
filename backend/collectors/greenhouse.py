"""Adapter for Greenhouse's documented public Job Board API."""
from __future__ import annotations
from backend.collectors.base import BaseCollector, CollectorError
from backend.normalization import RawOpportunity, clean_html, is_student_opportunity

class GreenhouseCollector(BaseCollector):
    def __init__(self, board: str, timeout: float = 20.0):
        super().__init__(timeout); self.board = board; self.source_name = f"greenhouse:{board}"
    def collect(self) -> list[RawOpportunity]:
        board_data = self.get_json(f"https://boards-api.greenhouse.io/v1/boards/{self.board}")
        data = self.get_json(f"https://boards-api.greenhouse.io/v1/boards/{self.board}/jobs?content=true")
        if not isinstance(data, dict) or not isinstance(data.get("jobs"), list): raise CollectorError(f"{self.source_name}: unexpected response")
        organization = board_data.get("name", self.board) if isinstance(board_data, dict) else self.board
        results = []
        for job in data["jobs"]:
            content = job.get("content") or ""
            if not is_student_opportunity(job.get("title", ""), clean_html(content)): continue
            # Greenhouse exposes updated_at, not an original publication date.
            results.append(RawOpportunity(str(job["id"]), job["title"], organization, self.source_name, job["absolute_url"], (job.get("location") or {}).get("name"), content, None, job))
        return results
