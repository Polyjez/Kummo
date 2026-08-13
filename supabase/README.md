# Supabase

Schema migrations, seed data, and local-stack config for Kummo, managed with the [Supabase CLI](https://supabase.com/docs/guides/local-development/cli/getting-started) via `pnpm exec supabase` (it's a `devDependency`, see root `package.json`). Running a local Supabase instance is optional — migrations can be authored and applied directly against the hosted cloud project without Docker.

## Layout

```
supabase/
  config.toml       # local stack config (ports, auth, studio, etc.) — committed
  migrations/        # timestamped, ordered SQL migrations — committed
  seed.sql           # dev-only seed data, only applied on a local `db reset` — committed
  .branches, .temp    # CLI-managed local state — gitignored
```

## Migrations

Each file in `migrations/` is a plain SQL script, applied in filename order. Filenames are timestamp-prefixed (`YYYYMMDDHHMMSS_description.sql`) so ordering is unambiguous and matches when they were created.

Current migrations:
- `20260613000000_initial.sql` — initial schema (`shops`, `activities`, `bookings`, `children`, …).
- `20260614172123_column-normalization.sql` — renames columns/constraints to consistent `lower_snake_case`.
- `20260614172525_table-id-fks.sql` — drops stray defaults on FK columns.
- `20260614172909_shops-telefon.sql` — renames `shops.telefon` → `shops.phone` (French → English column names, see root `CLAUDE.md`).

### Creating a new migration

```bash
pnpm exec supabase migration new <description>
```

Creates an empty, timestamped file in `migrations/`. No local stack needed for this step — write plain SQL (DDL/DML) into the file.

### Applying migrations to the hosted (cloud) project

This is the normal path — no Docker or local Postgres involved:

```bash
pnpm exec supabase login                                    # once per machine
pnpm exec supabase link --project-ref xusuvidhmuyzpfrtxutd   # once per checkout
pnpm exec supabase db push                                   # applies any un-run migrations
```

`db push` compares `migrations/` against the migration history table on the linked remote project and applies whatever hasn't run yet, in order. `seed.sql` is **not** applied by `db push` — it only runs locally (see below).

### Applying migrations locally (optional)

Useful for testing a migration before pushing it to cloud. Requires Docker.

```bash
pnpm exec supabase start     # boots local Postgres/Studio/Auth and applies all migrations to a fresh DB
pnpm exec supabase db reset  # drops the local DB, replays all migrations, then runs seed.sql
```

`./start-kummo.sh local` wraps `supabase start` and also patches `static/js/config.js` with the local URL/anon key — see the root `CLAUDE.md` for the local vs. cloud run modes.

You can also iterate against a running local DB (Studio or `psql`) and generate a migration from the diff:

```bash
pnpm exec supabase db diff -f <description>
```

### Conventions

- One logical schema change per migration file; keep them small and reviewable.
- Never edit a migration that has already been applied to the hosted project — add a new migration instead (migrations are an append-only log).
- Column names in migrations must match the English, `lower_snake_case` names documented in the root `CLAUDE.md` (`title`, `price`, `name`, `address`, `duration`, `picture`, `activity_type`, `age_group`, `participants_max`, `shop_id`, etc.).

## Seed data

`seed.sql` is dev-only fixture data (Berlin shops/activities). It only runs against a **local** instance (first `supabase start` or `supabase db reset`) — never against the hosted cloud project.

## Config

`config.toml` defines the local stack's ports and service settings (API on `54321`, Postgres on `54322`, etc.) — see the comments in the file or the [CLI config reference](https://supabase.com/docs/guides/local-development/cli/config). It's only relevant if you run the stack locally, and is committed so the whole team boots an identical local stack when they do.
