# ADR 0004 — Schema migrations: the Supabase CLI as the single DDL chain

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-08-16 |
| **Deciders** | Architect |
| **Amends** | [ADR 0003 — Persistence layer: SQLAlchemy 2.0 + Alembic](0003-persistence-sqlalchemy.md), §*Migration strategy* only. The SQLAlchemy half of 0003 stands unchanged. |

## Context

ADR 0003 chose Alembic as the single migration chain, on the reasoning that keeping DDL inside the codebase avoids a fragmented history and limits coupling to Supabase tooling. In practice the opposite happened: because Supabase Auth, the local stack and the hosted project are all driven by the Supabase CLI, the CLI has its own migration chain that cannot be given up. The project ran **two** chains against one database — `supabase_migrations.schema_migrations` and `kummo.alembic_version` — with a boundary rule ("CLI owns roles, extensions and anything outside `kummo`; Alembic owns the application tables") that had to be written down and remembered.

The split produced concrete friction rather than theoretical cost:

- **Ordering was non-obvious.** `supabase db reset` replays only the CLI migrations, so the `kummo` tables did not exist when the CLI wanted to seed. This forced `[db.seed] enabled = false` and a bespoke `kummo-db-reset` task chaining reset → `alembic upgrade head` → seed, in an order a newcomer had no way to infer.
- **Only one chain was visible in the Supabase dashboard.** The half that defined the application tables was not.
- **The split cost a second DB role and a second connection string** (`kummo_migrator`, `MIGRATION_DATABASE_URL`) whose only purpose was giving Alembic its own DDL identity.
- **`alembic/env.py` was ~70 lines of pure scaffolding** — schema filters, `version_table_schema`, async-engine plumbing, four import-for-side-effect lines — whose entire job was teaching Alembic not to touch `auth.*`.

Set against that, Alembic's real benefit is autogenerate from the ORM models. At the time of this decision the application schema was four tables and one revision.

The governing constraint for this project is a skeleton that a next developer can pick up: standard, small, and with one way to do each thing. Two migration tools is the single largest violation of that in the repository.

### Options considered

| Option | Verdict | Rationale |
|---|---|---|
| **Supabase CLI SQL migrations only** | **Selected** | One chain, one history table, one ordering, fully visible in the dashboard. Plain SQL is readable without knowing a tool. `supabase db reset` becomes the entire local rebuild. Cost: loses autogenerate (see *Consequences*). |
| Alembic only | Rejected | Not reachable. The CLI chain is required for Auth config, extensions and the hosted project; removing it is not an option, so "Alembic only" is really "Alembic plus the CLI" — the status quo. |
| Keep both, as ADR 0003 specified | Rejected | The costs above are recurring and land on every newcomer, while the benefit (autogenerate over four tables) is small and replaceable. |

## Decision

**All DDL is a Supabase CLI migration** in `supabase/migrations/`, plain SQL, applied in filename order. Alembic is removed from the project.

- SQLAlchemy remains the runtime persistence toolkit — ADR 0003's primary decision is untouched. The entities in `*/data_model.py` are now a *description* of the schema, not its source.
- **`kummo_migrator` is removed entirely.** A separate owning role only made sense while a second tool needed its own DDL identity. Objects are now owned by whichever role the CLI connects as, and each migration adding a table ends with an explicit `grant … to kummo_app`.
- **Migrations never change role.** The CLI records each applied migration with an `INSERT` into `supabase_migrations.schema_migrations` inside that migration's own transaction; a `set local role` (or a `reset role`, which discards the session role the CLI set up) is still in effect when that `INSERT` runs and fails it with `permission denied for schema supabase_migrations` — *after* the DDL has committed its work, leaving the target half-migrated. This is not a style preference; it is the constraint that decided the role model.
- `MIGRATION_DATABASE_URL` is removed — the backend holds one database URL, the DML-only `kummo_app`.
- Seeding returns to the CLI (`[db.seed] enabled = true`), so `supabase db reset` rebuilds the local database in one command and the `kummo-db-*` console scripts are removed.

### Replacing autogenerate

Drift between the hand-written schema and the SQLAlchemy entities would otherwise surface as a query error at runtime. It is caught instead by an integration test (`backend/tests/integration/test_schema_matches_data_model.py`) that reflects the live `kummo` schema and compares it, table and column, against `Entity.metadata`. This is a stronger check than autogenerate: it verifies the database that was actually migrated rather than a generated diff. `supabase db diff` covers the interactive "what did I change" case.

## Consequences

- One migration history, visible in the Supabase dashboard, applied the same way locally (`supabase db reset` / `migration up`) and to the hosted project (`db push`).
- Onboarding drops a tool. Reading the schema's history requires only SQL.
- Removed: `backend/alembic/`, `alembic.ini`, `src/kummo/tasks.py`, the `alembic` dependency, `MIGRATION_DATABASE_URL`, and the `[project.scripts]` block.
- Transcribing the schema by hand surfaced `kummo.bookings` as created-but-never-used — no route touched it, and the frontend keeps bookings in localStorage. It is dropped along with its entity and seed rows, and returns with the feature. Autogenerate would have carried it forward silently; writing the DDL out is what made it visible.
- **Cost:** schema changes are now two edits — the migration and the matching `data_model.py` — instead of one generated from the other. The drift test makes forgetting the second a test failure rather than a production error.
- **Cost:** no generated `downgrade()`. Rollback is a new forward migration, which is the operationally safer habit anyway.
- **Incident, 2026-08-16.** The first `db push` of this chain onto the hosted project applied `20260804155602` and `20260815120000`, then failed on `20260816200000` for the role-switch reason above. Because `20260815120000` drops the legacy `public.*` tables and the hosted project had never actually been migrated to `kummo` (Alembic was only ever run locally), the push destroyed the legacy tables without creating their replacements. Two lessons are baked into this ADR: migrations must not change role, and a chain containing a destructive migration must never be pushed to an environment whose current state has not been verified first. `supabase/snippets/reset-hosted-migration-state.sql` is the cleanup.
- Revisit if the schema grows large enough that hand-written DDL becomes the bottleneck. Reintroducing Alembic later is a `revision --autogenerate` against an existing database — the door is not closed.
