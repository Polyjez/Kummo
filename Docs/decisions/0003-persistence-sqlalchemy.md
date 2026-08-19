# ADR 0003 — Persistence layer: SQLAlchemy 2.0 + Alembic

| | |
|---|---|
| **Status** | Accepted — *migration strategy amended by [ADR 0004](0004-supabase-cli-single-migration-chain.md)* |
| **Date** | 2026-07 |
| **Deciders** | Tech lead |
| **Resolves** | The persistence open point left by the backend framework choice (*Backend Framework Choice: FastAPI vs. Alternatives*, §5 — not yet captured as an ADR in this repo) |
| **Open questions** | [open_questions/technical/persistence.md](../open_questions/technical/persistence.md) |

## Context

Supabase is used strictly as managed PostgreSQL + Auth/Storage/Realtime; FastAPI is the sole owner of business logic, connecting via the service role. Critical operations — booking creation under concurrent demand, payment state transitions, `audit_events` emission — require real transactional control (locking, atomic multi-step commits), which is not reliably available through Supabase's PostgREST-based Python client. A direct connection to Postgres, via a proper Python database toolkit, is required for the business logic layer.

The Supabase Python client remains appropriate for Storage and Auth, where PostgREST's request/response model is not a constraint.

### Options considered

| Option | Verdict | Rationale |
|---|---|---|
| **SQLAlchemy 2.0 (async)** | **Selected** | Long-standing standard for Python DB access; async-native since the 2.0 rewrite (asyncpg/psycopg). Full transactional control (row-level locking, multi-statement atomic commits). Largest ecosystem — minimizes the risk of a future maintainer being stuck without docs/support. Pairs natively with Alembic. Trade-off: real learning curve around session management, front-loaded rather than recurring. |
| SQLModel | Not primary | A thin convenience layer *on top of* SQLAlchemy (single class for table + Pydantic schema), not an independent alternative; still requires understanding SQLAlchemy, and lacks maturity for complex relationships. May be revisited for simple DTO-like models. |
| Tortoise ORM | Rejected | Async-first, concise Django-style syntax, but migration tooling (Aerich) is materially less mature than Alembic and the ecosystem is significantly smaller — works against maintainability-after-handoff. |
| Piccolo | Rejected | Strong compile-time type safety, but migrations are hand-written (no autogenerate), rollbacks defined manually, smaller community, not a widely taught standard. |
| Supabase Python client (PostgREST) alone | Rejected for business logic | Adequate for Storage/Auth; no native row-level locking or atomic multi-statement transactions, required given the race-condition risk on concurrent bookings and payment integrity. |

## Decision

Adopt **SQLAlchemy 2.0 (async)** as the persistence toolkit for all business-logic tables (bookings, payments, matching, `audit_events`), connecting directly to Postgres rather than through PostgREST. Adopt **Alembic** as the single migration chain for the application-owned schema.

### Migration strategy: Alembic as single source of truth

> **Superseded by [ADR 0004](0004-supabase-cli-single-migration-chain.md).** This section is
> kept for the record. In practice the Supabase CLI's own migration chain could not be given
> up, so the project ran two chains against one database; ADR 0004 collapses all DDL onto the
> CLI. The SQLAlchemy decision above is unaffected.

Alembic is a schema migration tool only — it compares the state declared by SQLAlchemy models against the actual DB schema and generates versioned `upgrade()`/`downgrade()` scripts. It is the single source of truth for the entire Postgres schema, including objects outside the ORM's native scope:

- **Extensions** (PostGIS, pgvector): declared via `op.execute()` in dedicated Alembic migrations.
- **RLS policies**: where still required for Supabase-native Storage/Auth access patterns, defined in Alembic via raw SQL rather than the Supabase CLI, to avoid a fragmented migration history.
- **Auth-related objects**: authentication is a separate module. Supabase-native objects that support it (`auth` schema, associated triggers) are **not** managed by the application's Alembic chain — they remain under Supabase's own management, keeping a clear boundary between application-owned schema and Supabase-owned Auth internals.

## Consequences

- Schema ownership and evolution stay inside the codebase, versioned alongside the code that depends on it.
- Coupling to Supabase-specific tooling is limited to Storage/Auth only.
- Relies on the most mature and widely documented option in the current Python ecosystem — a direct match for Kummo's handoff-to-Python-team requirement.
- **Cost:** an initial learning curve around SQLAlchemy's session and transaction model, paid once when establishing the project's session/dependency patterns.
