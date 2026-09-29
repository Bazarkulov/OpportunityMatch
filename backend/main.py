"""OpportunityMatch FastAPI application."""
from __future__ import annotations
import hmac
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from backend.collection import refresh_opportunities
from backend.config import get_settings
from backend.database import create_tables, get_db
from backend.dependencies import get_current_user
from backend.eligibility import evaluate_eligibility
from backend.matching import score_relevance
from backend.models import Opportunity, SavedOpportunity, StudentProfile, User
from backend.schemas import AuthRequest, AuthResponse, CollectionResult, OpportunityOut, ProfileOut, ProfileUpdate, RecommendationOut, UserOut
from backend.security import create_token, hash_password, verify_password

@asynccontextmanager
async def lifespan(_: FastAPI):
    create_tables(); yield

app = FastAPI(title="OpportunityMatch API", version="1.0.0", lifespan=lifespan)
settings = get_settings()
app.add_middleware(CORSMiddleware, allow_origins=settings.csv(settings.cors_origins), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health(): return {"status": "ok"}

@app.post("/api/auth/register", response_model=AuthResponse, status_code=201)
def register(payload: AuthRequest, db: Session = Depends(get_db)):
    user = User(email=str(payload.email).casefold(), password_hash=hash_password(payload.password)); db.add(user)
    try: db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(409, "An account with this email already exists")
    db.refresh(user); return AuthResponse(access_token=create_token(user.id), user=user)

@app.post("/api/auth/login", response_model=AuthResponse)
def login(payload: AuthRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(payload.email).casefold()))
    if user is None or not verify_password(payload.password, user.password_hash): raise HTTPException(401, "Incorrect email or password")
    return AuthResponse(access_token=create_token(user.id), user=user)

@app.get("/api/auth/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)): return user

@app.get("/api/profile", response_model=ProfileOut)
def get_profile(user: User = Depends(get_current_user)):
    if user.profile is None: raise HTTPException(404, "Profile not created")
    return user.profile

@app.put("/api/profile", response_model=ProfileOut)
def put_profile(payload: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    values = payload.model_dump()
    if user.profile is None: profile = StudentProfile(user_id=user.id, **values); db.add(profile)
    else:
        profile = user.profile
        for key, value in values.items(): setattr(profile, key, value)
    db.commit(); db.refresh(profile); return profile

def opportunity_out(opportunity: Opportunity, saved: bool = False) -> OpportunityOut:
    result = OpportunityOut.model_validate(opportunity); result.saved = saved; return result

@app.get("/api/opportunities", response_model=list[OpportunityOut])
def list_opportunities(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    saved = set(db.scalars(select(SavedOpportunity.opportunity_id).where(SavedOpportunity.user_id == user.id)).all())
    rows = db.scalars(select(Opportunity).where(Opportunity.active.is_(True)).order_by(Opportunity.deadline.asc().nullslast(), Opportunity.title).offset(offset).limit(limit)).all()
    return [opportunity_out(row, row.id in saved) for row in rows]

@app.get("/api/opportunities/{opportunity_id}", response_model=OpportunityOut)
def get_opportunity(opportunity_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    opportunity = db.get(Opportunity, opportunity_id)
    if opportunity is None: raise HTTPException(404, "Opportunity not found")
    saved = db.scalar(select(SavedOpportunity.id).where(SavedOpportunity.user_id == user.id, SavedOpportunity.opportunity_id == opportunity_id)) is not None
    return opportunity_out(opportunity, saved)

@app.get("/api/recommendations", response_model=list[RecommendationOut])
def recommendations(limit: int = Query(50, ge=1, le=200), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.profile is None: raise HTTPException(409, "Create a profile before requesting recommendations")
    saved = set(db.scalars(select(SavedOpportunity.opportunity_id).where(SavedOpportunity.user_id == user.id)).all())
    results = []
    for opportunity in db.scalars(select(Opportunity).where(Opportunity.active.is_(True))).all():
        eligibility = evaluate_eligibility(user.profile, opportunity)
        if eligibility["status"] == "ineligible": continue
        results.append({"opportunity": opportunity_out(opportunity, opportunity.id in saved), "eligibility": eligibility, "match": score_relevance(user.profile, opportunity)})
    results.sort(key=lambda item: (-item["match"]["overall_score"], item["opportunity"].title))
    return results[:limit]

@app.get("/api/saved", response_model=list[OpportunityOut])
def list_saved(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Opportunity).join(SavedOpportunity).where(SavedOpportunity.user_id == user.id).order_by(SavedOpportunity.created_at.desc())).all()
    return [opportunity_out(row, True) for row in rows]

@app.post("/api/saved/{opportunity_id}", status_code=201)
def save_opportunity(opportunity_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if db.get(Opportunity, opportunity_id) is None: raise HTTPException(404, "Opportunity not found")
    existing = db.scalar(select(SavedOpportunity).where(SavedOpportunity.user_id == user.id, SavedOpportunity.opportunity_id == opportunity_id))
    if existing is None: db.add(SavedOpportunity(user_id=user.id, opportunity_id=opportunity_id)); db.commit()
    return {"saved": True}

@app.delete("/api/saved/{opportunity_id}", status_code=204)
def unsave_opportunity(opportunity_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.scalar(select(SavedOpportunity).where(SavedOpportunity.user_id == user.id, SavedOpportunity.opportunity_id == opportunity_id))
    if existing: db.delete(existing); db.commit()

@app.post("/api/collection/refresh", response_model=CollectionResult)
def refresh_collection(x_collection_key: str | None = Header(None), db: Session = Depends(get_db)):
    expected = settings.collection_admin_token
    if not expected or not x_collection_key or not hmac.compare_digest(expected, x_collection_key): raise HTTPException(status.HTTP_403_FORBIDDEN, "Collection endpoint is disabled or the key is invalid; use the local CLI instead")
    run = refresh_opportunities(db)
    return CollectionResult(run_id=run.id, status=run.status, sources_succeeded=run.sources_succeeded, sources_failed=run.sources_failed, records_seen=run.records_seen, records_upserted=run.records_upserted, errors=run.errors or [])
