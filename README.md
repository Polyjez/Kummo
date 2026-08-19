# Kummo

A B2B2C web app for discovering and booking family- and senior-friendly activities in Berlin.

- **Frontend** — a static multi-page site (`static/`): vanilla JS, no framework, no bundler.
- **Backend** — FastAPI (`backend/`), talking to Postgres directly (SQLAlchemy async + asyncpg).
- **Supabase** — used for **Auth only** (GoTrue) and as the managed Postgres. The browser never talks to Supabase; credentials stay server-side.

Documentation (product requirements, engineering specification, decision records) lives in
[`Docs/`](Docs/README.md). Start with [what is built and what remains](Docs/engineering/implementation-status.md).

## Prerequisites

| Tool | Used for |
|---|---|
| [`uv`](https://docs.astral.sh/uv/getting-started/installation/) | Python 3.12 backend (dependencies, runner) |
| `pnpm` | Supabase CLI, frontend tests |
| **Docker** | the local Supabase stack — see the Podman note below |

You also need an env file per environment at the **repo root**: `.env.local`, `.env.prod`.
Each must define `SUPABASE_URL`, `SUPABASE_API_KEY` and `DATABASE_URL` — see
[`backend/.env.example`](backend/.env.example).

> **Podman is not currently usable for the local stack.** With Podman 6.1.0 the Supabase
> CLI (2.111.0) fails to bring the stack up, even with
> `export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/podman/podman.sock`. Use Docker for
> `supabase start` until this is resolved; cloud mode (`prod`) needs no container runtime at all.

## Running the app

```sh
./start-kummo.sh local    # or: pnpm start
./start-kummo.sh prod     # or: pnpm start:prod
```

Then open <http://localhost:8000>. Do not open the HTML files with `file://` — the `/api/*`
routes will not resolve.

| Mode | Database | Backend | Migrations |
|---|---|---|---|
| `local` (default) | Supabase in Docker, started by the script | `fastapi dev` (hot-reload) | applied automatically |
| `prod` | the hosted Supabase project | `fastapi run` | **not** applied automatically |

Windows: `start-kummo.bat [env]`.

### Starting the backend by hand

The env file lives at the repo root, not in `backend/`, and `--env-file` is a `uv run` flag —
it must come *before* the command:

```sh
cd backend
uv sync --all-groups
uv run --env-file ../.env.local fastapi dev src/kummo/main.py
```

## Database

The Supabase CLI is the database task runner. `supabase/migrations/` is the single DDL chain —
there is no Alembic.

```sh
pnpm exec supabase migration new "describe the change"   # then write the SQL
pnpm exec supabase migration up                          # apply pending migrations
pnpm db:reset                                            # rebuild from scratch + supabase/seed.sql
pnpm db:start / pnpm db:stop                             # start / stop the local stack
pnpm exec supabase status                                # local URLs and keys
```

A schema change is **two edits**: the migration SQL *and* the matching feature `data_model.py`.
`backend/tests/integration/test_schema_matches_data_model.py` reflects the live schema and fails
if the two diverge.

## Tests

```sh
cd backend
uv run pytest -m 'not integration'   # route/unit tests, no database needed
uv run pytest -m integration         # real queries against the local Supabase Postgres
```

```sh
pnpm install && pnpm test            # frontend regression tests (Vitest + jsdom)
pnpm run test:watch
```

## Documentation site

```sh
./docs-serve.sh [port]    # MkDocs Material, live reload; bootstraps Docs/.venv on first run
```
