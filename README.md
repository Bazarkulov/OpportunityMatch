# OpportunityMatch

OpportunityMatch is a locally runnable student opportunity discovery product. It collects current public listings, keeps unknown requirements explicit, evaluates eligibility separately from relevance, and explains personalized recommendations.

## Architecture

```text
Greenhouse / Lever public APIs → source adapters → raw listings
→ deterministic normalization → validation/deduplication/lifecycle updates
→ SQLite locally or PostgreSQL → eligibility + relevance ranking
→ FastAPI → Next.js
```

The default SQLite setup needs no cloud account. PostgreSQL is supported through `DATABASE_URL`. Authentication uses signed bearer tokens and salted PBKDF2 password hashes. Supabase is not required or currently integrated.

## Prerequisites and quick start

Use Python 3.11+ and Node.js 20+. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m backend.init_db
python -m backend.collect
uvicorn backend.main:app --reload
```

In a second terminal:

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`. Register, create a profile, browse recommendations, open explanations and source links, and save opportunities. API documentation is at `http://localhost:8000/docs`. Change `AUTH_SECRET` before storing real accounts.

## PostgreSQL

Optionally run `docker compose up -d postgres`, then set:

```dotenv
DATABASE_URL=postgresql+psycopg://opportunitymatch:opportunitymatch@localhost:5432/opportunitymatch
```

Run `python -m backend.init_db`. `migrations/001_initial.sql` is the equivalent reference schema for managed PostgreSQL.

## Collection

```bash
source .venv/bin/activate
python -m backend.collect
```

Defaults verified during development: Figma (Greenhouse), and Xcimer Energy, ANYbotics, and Hermeus (Lever). Configure comma-separated `GREENHOUSE_BOARDS` and `LEVER_SITES` values in `.env`. The command is suitable for cron. `POST /api/collection/refresh` can be enabled with `COLLECTION_ADMIN_TOKEN` and requires `X-Collection-Key`.

## Matching

Eligibility evaluates degree, explicit major restrictions, nationality, normalized GPA, and language. It returns `eligible`, `ineligible`, or `uncertain` plus passed, failed, and unknown explanations. Omitted requirements cause uncertainty, not rejection.

Weights in `backend/matching.py`: exact skills 20%, semantic skills 15%, major/field 20%, interests/topics 20%, type 10%, location 10%, remote 5%. The default offline semantic provider creates hashed text vectors, expands a transparent synonym map, and uses cosine similarity. `SimilarityProvider` is the extension point for Sentence Transformers; the optional dependency is recorded in `requirements-semantic.txt`, but that large-model path is not enabled or claimed as tested.

## Tests and checks

```bash
source .venv/bin/activate
pytest -q
python -m scripts.smoke_test
cd frontend
npm run typecheck
npm run lint
npm run build
npm audit
```

## API

- Auth: `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- Profile: `GET/PUT /api/profile`
- Opportunities: `GET /api/opportunities`, `GET /api/opportunities/{id}`
- Recommendations: `GET /api/recommendations`
- Saves: `GET /api/saved`, `POST/DELETE /api/saved/{id}`
- Operations: `POST /api/collection/refresh`, `GET /health`

User data is always scoped from the bearer token; callers cannot choose another user ID.

## Troubleshooting and boundaries

- Empty feed: run collection and create a profile.
- Collector failure: inspect per-source errors; other adapters continue.
- CORS error: include the frontend in `CORS_ORIGINS`.
- Frontend cannot reach API: set `NEXT_PUBLIC_API_URL` before starting Next.js.
- Database error: check `DATABASE_URL`, then run `python -m backend.init_db`.

Normalization is deliberately conservative. It cannot understand every prose requirement. Nationality/language restrictions remain unknown unless safely extracted. Publication dates stay null if a source exposes only an update time. Applications are completed on the publisher's original page.
