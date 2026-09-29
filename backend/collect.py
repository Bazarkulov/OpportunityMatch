"""Manual opportunity refresh command: python -m backend.collect."""
import json
import logging
from backend.collection import refresh_opportunities
from backend.database import SessionLocal, create_tables

def main() -> None:
    logging.basicConfig(level=logging.INFO)
    create_tables()
    with SessionLocal() as db:
        run = refresh_opportunities(db)
        print(json.dumps({"run_id": run.id, "status": run.status, "sources_succeeded": run.sources_succeeded, "sources_failed": run.sources_failed, "records_seen": run.records_seen, "records_upserted": run.records_upserted, "errors": run.errors}, indent=2))

if __name__ == "__main__": main()
