# OpportunityMatch data model

The runtime model is defined in `backend/models.py` and persisted through SQLAlchemy to SQLite or PostgreSQL. API contracts are in `backend/schemas.py`; `migrations/001_initial.sql` is the PostgreSQL reference migration.

Unknown extracted requirements are stored as `NULL`. An empty list means a source explicitly has no restriction, while `NULL` means the source did not provide enough information. Raw source text and source URLs are retained for auditability.

`student profile → three-state eligibility → discard ineligible → hybrid relevance score → ranked feed`

Eligibility and relevance are separate outputs. Eligible and uncertain opportunities can appear in the feed. Explicit failures do not.
