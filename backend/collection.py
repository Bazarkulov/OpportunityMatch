"""Fault-isolated collection, normalization, deduplication, and upsert pipeline."""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from backend.collectors.base import BaseCollector
from backend.collectors.greenhouse import GreenhouseCollector
from backend.collectors.lever import LeverCollector
from backend.config import get_settings
from backend.models import CollectionRun, Opportunity
from backend.normalization import normalize

logger = logging.getLogger(__name__)

def configured_collectors() -> list[BaseCollector]:
    settings = get_settings()
    return [GreenhouseCollector(x, settings.collector_timeout_seconds) for x in settings.csv(settings.greenhouse_boards)] + [LeverCollector(x, settings.collector_timeout_seconds) for x in settings.csv(settings.lever_sites)]

def refresh_opportunities(db: Session, collectors: list[BaseCollector] | None = None) -> CollectionRun:
    run = CollectionRun(); db.add(run); db.commit(); db.refresh(run)
    for collector in collectors or configured_collectors():
        try:
            raw_records = collector.collect(); run.sources_succeeded += 1; run.records_seen += len(raw_records)
            seen: set[str] = set()
            for raw in raw_records:
                values = normalize(raw); seen.add(values["external_id"])
                existing = db.scalar(select(Opportunity).where(Opportunity.source == values["source"], Opportunity.external_id == values["external_id"]))
                if existing is None:
                    duplicate = db.scalar(select(Opportunity).where(Opportunity.fingerprint == values["fingerprint"], Opportunity.active.is_(True)))
                    if duplicate:
                        duplicate.last_verified_at = values["last_verified_at"]
                        continue
                    db.add(Opportunity(**values))
                else:
                    for key, value in values.items(): setattr(existing, key, value)
                run.records_upserted += 1
            if seen:
                db.execute(update(Opportunity).where(Opportunity.source == collector.source_name, Opportunity.external_id.not_in(seen)).values(active=False))
            db.commit()
        except Exception as exc:
            db.rollback(); run = db.get(CollectionRun, run.id)
            run.sources_failed += 1; run.errors = [*(run.errors or []), f"{collector.source_name}: {exc}"]
            logger.exception("Collector failed: %s", collector.source_name); db.commit()
    run = db.get(CollectionRun, run.id); run.completed_at = datetime.now(timezone.utc)
    run.status = "completed" if run.sources_failed == 0 else ("partial" if run.sources_succeeded else "failed")
    db.commit(); db.refresh(run); return run
