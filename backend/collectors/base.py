"""Collector interface and shared HTTP behavior."""
from __future__ import annotations
from abc import ABC, abstractmethod
import httpx
from backend.normalization import RawOpportunity

class CollectorError(RuntimeError): pass

class BaseCollector(ABC):
    source_name: str
    def __init__(self, timeout: float = 20.0): self.timeout = timeout
    def get_json(self, url: str) -> dict | list:
        try:
            response = httpx.get(url, timeout=self.timeout, follow_redirects=True, headers={"User-Agent": "OpportunityMatch/1.0 (+local educational project)"})
            response.raise_for_status(); return response.json()
        except (httpx.HTTPError, ValueError) as exc: raise CollectorError(f"{self.source_name}: {exc}") from exc
    @abstractmethod
    def collect(self) -> list[RawOpportunity]: ...
