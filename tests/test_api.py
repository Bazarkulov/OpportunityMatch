from backend.database import SessionLocal
from backend.models import Opportunity
from backend.normalization import RawOpportunity, normalize
def auth(client):
    response=client.post("/api/auth/register",json={"email":"student@example.com","password":"strong-password"}); assert response.status_code==201; return {"Authorization":f"Bearer {response.json()['access_token']}"}
def seed():
    with SessionLocal() as db: db.add(Opportunity(**normalize(RawOpportunity("live-1","Robotics Research Internship","University Robotics Lab","test-public-api","https://example.edu/jobs/live-1","Munich, Germany","Undergraduate research internship using Python, ROS2 and Computer Vision.")))); db.commit()
def test_complete_authenticated_api_workflow(client):
    headers=auth(client); seed(); assert client.get("/api/recommendations",headers=headers).status_code==409
    profile={"degree_level":"Bachelor's","university":"Example University","major":"Robotics","academic_year":"Third year","nationality":"Kazakhstani","gpa":3.7,"gpa_scale":4.0,"languages":{"English":"Professional Fluency"},"skills":["Python","ROS2","Computer Vision"],"interests":["Robotics"],"preferred_opportunity_types":["Research Internship"],"preferred_locations":["Germany"],"remote_preference":False,"extra_data":{}}
    assert client.put("/api/profile",headers=headers,json=profile).status_code==200
    recommendations=client.get("/api/recommendations",headers=headers); assert recommendations.status_code==200; assert len(recommendations.json())==1; assert recommendations.json()[0]["eligibility"]["status"]=="uncertain"
    opportunity_id=recommendations.json()[0]["opportunity"]["id"]; assert client.get(f"/api/opportunities/{opportunity_id}",headers=headers).status_code==200; assert client.post(f"/api/saved/{opportunity_id}",headers=headers).status_code==201; assert len(client.get("/api/saved",headers=headers).json())==1; assert client.delete(f"/api/saved/{opportunity_id}",headers=headers).status_code==204; assert client.get("/api/saved",headers=headers).json()==[]
def test_user_data_is_scoped(client):
    first=auth(client); seed(); opportunity_id=client.get("/api/opportunities",headers=first).json()[0]["id"]; client.post(f"/api/saved/{opportunity_id}",headers=first)
    response=client.post("/api/auth/register",json={"email":"other@example.com","password":"strong-password"}); second={"Authorization":f"Bearer {response.json()['access_token']}"}; assert client.get("/api/saved",headers=second).json()==[]
def test_protected_routes_require_auth(client): assert client.get("/api/profile").status_code==401
