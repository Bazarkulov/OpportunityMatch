from sqlalchemy import select
from backend.collection import refresh_opportunities
from backend.database import SessionLocal
from backend.models import Opportunity
from backend.normalization import RawOpportunity
class FakeCollector:
    source_name="fake:public"
    def collect(self): return [RawOpportunity("one","Research Intern","Real University","fake:public","https://example.edu/jobs/one","Remote","Undergraduate Python research internship")]
def test_refresh_upserts_instead_of_duplicating():
    with SessionLocal() as db:
        first=refresh_opportunities(db,[FakeCollector()]); second=refresh_opportunities(db,[FakeCollector()]); assert first.records_upserted==1 and second.records_upserted==1; assert len(db.scalars(select(Opportunity)).all())==1
