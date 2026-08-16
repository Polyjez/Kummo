# Supabase

Local-stack config, auth/role migrations and dev seed data for Kummo, managed with the
[Supabase CLI](https://supabase.com/docs/guides/local-development/cli/getting-started) via
`pnpm exec supabase` (it's a `devDependency`, see the root `package.json`).

**Supabase is used for Auth only.** The application data lives in the `kummo` schema, which the
FastAPI backend reaches over a direct Postgres connection (SQLAlchemy async + asyncpg) — not
through PostgREST. The browser never talks to Supabase, and there is no RLS.

## Two migration tools, two owners

| Directory | Runs as | Owns |
|---|---|---|
| `supabase/migrations/` (CLI) | `postgres` | roles, the `kummo` schema container, auth config, extensions — anything *outside* the `kummo` tables |
| `backend/alembic/versions/` | `kummo_migrator` | every application table in the `kummo` schema |

**Do not create application tables from a CLI migration.** New tables go through Alembic
(`cd backend && uv run alembic revision --autogenerate -m "..."`).

Two database roles are created by `20260804155602_kummo-backend.sql`:

- `kummo_migrator` — DDL only, used by Alembic (`MIGRATION_DATABASE_URL`). It owns the `kummo`
  schema. `postgres` is granted the role only long enough to create the schema and set default
  privileges, then the membership is revoked, so the schema is only ever changed by Alembic.
- `kummo_app` — DML only, no DDL, no `BYPASSRLS`, used by the backend at runtime (`DATABASE_URL`).
  Default privileges grant it `select/insert/update/delete` on anything `kummo_migrator` creates.

## Layout

```
supabase/
  config.toml        # local stack config (ports, auth, studio, …) — committed
  migrations/        # timestamped, ordered SQL migrations — committed
  seed.sql           # dev-only seed data, applied by `uv run kummo-db-seed` — committed
  snippets/          # one-off SQL run by hand against the hosted project — committed
  .branches, .temp   # CLI-managed local state — gitignored
```

## Migrations

Each file in `migrations/` is a plain SQL script, applied in filename order. Filenames are
timestamp-prefixed (`YYYYMMDDHHMMSS_description.sql`) so ordering is unambiguous.

Current migrations:

- `20260804155602_kummo-backend.sql` — creates the `kummo_migrator` / `kummo_app` roles and the
  `kummo` schema with its default privileges.
- `20260815120000_drop-legacy-public-tables.sql` — drops the old `public.shops` / `users` /
  `children` / `activities` / `bookings` tables that predate the move into `kummo`. A no-op on a
  fresh database; it matters only for databases provisioned before the move.

### Creating a new migration

```bash
pnpm exec supabase migration new <description>
```

Creates an empty, timestamped file in `migrations/`. No local stack needed for this step.

### Applying migrations locally

Requires Docker. The full rebuild is a backend task, because the order matters:

```bash
cd backend
uv run kummo-db-reset    # supabase db reset → alembic upgrade head → seed.sql
```

`supabase db reset` replays only the CLI migrations, and the `kummo` tables do not exist until
Alembic has run — which is also why `[db.seed] enabled = false` in `config.toml` and why
`seed.sql` is applied afterwards by `uv run kummo-db-seed` rather than by the CLI.

The individual steps, if you need them separately:

```bash
pnpm exec supabase start                        # boot Postgres/Studio/Auth, apply CLI migrations
cd backend && uv run alembic upgrade head       # create/update the kummo tables
cd backend && uv run kummo-db-seed              # load supabase/seed.sql
```

`./start-kummo.sh local` wraps `supabase start` + `alembic upgrade head` and then runs the
FastAPI dev server — see the root `CLAUDE.md` for the local vs. cloud run modes.

### Applying migrations to the hosted (cloud) project

```bash
pnpm exec supabase login                                     # once per machine
pnpm exec supabase link --project-ref xusuvidhmuyzpfrtxutd   # once per checkout
pnpm exec supabase db push                                   # applies any un-run CLI migrations
```

`db push` compares `migrations/` against the migration history table on the linked remote project
and applies whatever hasn't run yet. It does **not** run Alembic and does **not** apply `seed.sql`.
The `kummo` tables on the hosted project are created by running Alembic against
`MIGRATION_DATABASE_URL` from `.env.prod`; `./start-kummo.sh prod` does not do this for you.

### Conventions

- One logical schema change per migration file; keep them small and reviewable.
- Never edit a migration that has already been applied to the hosted project — add a new migration
  instead (migrations are an append-only log).
- Column names are English `lower_snake_case` and must match the names documented in the root
  `CLAUDE.md` (`title`, `price`, `name`, `address`, `duration`, `picture`, `activity_type`,
  `age_group`, `participants_max`, `vendor_id`, `client_id`, …).

## Seed data

`seed.sql` is dev-only fixture data (Berlin vendors, activities). It is idempotent — the rows carry
fixed UUIDs and are deleted before being re-inserted — and it uses `DELETE`, not `TRUNCATE`, because
`kummo_app` holds DML privileges only. It is applied by `uv run kummo-db-seed`, never against the
hosted project.

## Snippets

`snippets/` holds one-off SQL that is run by hand from the Supabase SQL editor and is not part of
any migration history. `migrate-public-to-kummo.sql` copies the legacy `public.*` rows into the
`kummo` schema on the hosted project; it must run *before*
`20260815120000_drop-legacy-public-tables.sql` and *after* Alembic has created the `kummo` tables.

## Config

`config.toml` defines the local stack's ports and service settings (API on `54321`, Postgres on
`54322`, Studio on `54323`, mail catcher on `54324`) — see the comments in the file or the
[CLI config reference](https://supabase.com/docs/guides/local-development/cli/config). Notable
Kummo-specific settings:

- `[auth] site_url = "http://localhost:8000"` and `additional_redirect_urls` include
  `http://localhost:8000/api/auth/callback` — the backend's OAuth callback route.
- `[auth.external.google] enabled = true` — the "Mit Google anmelden" flow on `login.html`.
- `[db.seed] enabled = false` — see the ordering note above.

It is committed so the whole team boots an identical local stack.
