# Persistence layer — open questions

Open point attached to [ADR 0003 — Persistence layer: SQLAlchemy 2.0 + Alembic](../../decisions/0003-persistence-sqlalchemy.md),
as amended by [ADR 0004 — the Supabase CLI as the single DDL chain](../../decisions/0004-supabase-cli-single-migration-chain.md).

| # | Question | Impact | Status |
|---|---|---|---|
| OQ-DB-1 | **Team conventions to front-load the SQLAlchemy learning curve.** Define the concrete conventions: session/dependency-injection pattern for FastAPI, and a review checklist for hand-written migrations (ADR 0004 replaced Alembic autogenerate with plain SQL, so column renames, backfills and non-null additions are written by hand and reviewed rather than generated). | Determines onboarding cost and migration safety; a poor convention here recurs across every migration. | Open — technical validation |
