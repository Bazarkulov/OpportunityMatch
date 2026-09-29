"""Exercise the database-backed user workflow against the FastAPI application."""
from __future__ import annotations
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import select
from backend.database import SessionLocal
from backend.main import app
from backend.models import Opportunity, User

def main() -> None:
    with SessionLocal() as db:
        if db.scalar(select(Opportunity.id).where(Opportunity.active.is_(True))) is None:
            raise SystemExit("No active opportunities. Run: python -m backend.collect")
    email = f"smoke-{uuid4()}@example.com"
    with TestClient(app) as client:
        registered = client.post("/api/auth/register", json={"email": email, "password": "smoke-test-password"}); registered.raise_for_status()
        headers = {"Authorization": f"Bearer {registered.json()['access_token']}"}
        profile = {"degree_level":"Bachelor's","university":"Smoke Test University","major":"Robotics","academic_year":"Third year","nationality":"Kazakhstani","gpa":3.7,"gpa_scale":4.0,"languages":{"English":"Professional Fluency"},"skills":["Python","ROS2","Computer Vision"],"interests":["Robotics","Artificial Intelligence"],"preferred_opportunity_types":["Internship","Research Internship"],"preferred_locations":["Germany","Switzerland"],"remote_preference":False,"extra_data":{}}
        saved_profile = client.put("/api/profile", headers=headers, json=profile); saved_profile.raise_for_status()
        feed = client.get("/api/recommendations", headers=headers); feed.raise_for_status()
        if not feed.json(): raise RuntimeError("The active collection produced no non-ineligible recommendations")
        top = feed.json()[0]; opportunity_id = top["opportunity"]["id"]
        detail = client.get(f"/api/opportunities/{opportunity_id}", headers=headers); detail.raise_for_status()
        saved = client.post(f"/api/saved/{opportunity_id}", headers=headers); saved.raise_for_status()
        shortlist = client.get("/api/saved", headers=headers); shortlist.raise_for_status(); assert any(x["id"] == opportunity_id for x in shortlist.json())
        removed = client.delete(f"/api/saved/{opportunity_id}", headers=headers); removed.raise_for_status()
        print({"workflow": "passed", "recommendations": len(feed.json()), "top_title": top["opportunity"]["title"], "top_score": top["match"]["overall_score"], "eligibility": top["eligibility"]["status"], "source_url": detail.json()["source_url"]})
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        if user: db.delete(user); db.commit()

if __name__ == "__main__": main()
