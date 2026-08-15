# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Kummo is a B2B2C web app for discovering and booking family/senior-friendly activities in Berlin. The full product vision lives in `README.md` (the PRD), which describes a *Glide* (no-code) MVP. **The actual codebase does not use Glide** — it is a static multi-page site (`static/`) served by a **FastAPI** backend (`backend/`). The backend talks to Postgres directly (SQLAlchemy async + asyncpg) and uses **Supabase** for Auth (GoTrue) only. Treat the PRD as product intent, not as a description of the current implementation.

## Language rules

- **English** for everything developer-facing: code (identifiers, function/variable names), comments, documentation, commit messages, `console.log` debug output, and test descriptions.
- **German only for UI** — anything an end user sees: rendered page text, `alert()` messages, button labels, and the German `echo` lines in the launcher scripts.
- **DB-mapped field names mirror the `kummo` schema columns**: `title`, `price`, `name`, `address`, `duration`, `picture`, `activity_type`, `age_group`, `participants_max`, `vendor_id`, etc. These are now English to match the actual columns — keep them spelled exactly as the column. There is **no `disponibilites`/availability column** in the schema; code that referenced it is guarded as optional, and the availability form field on `business.html` is not persisted (pending a product/schema decision).
- Historical note: the code (and originally the DB columns) was French — `titre`→`title`, `prix`→`price`, `nom`→`name`, `adresse`→`address`, `duree`→`duration`, `photo`→`picture`, `type_activites`→`activity_type` (and earlier `magasins`→`shops`, `activites`→`activities`). All identifiers are now English. If you find leftover French, translate it.
- Later rename: `shops`→`vendors` (a vendor is the business *and* the shop), `users`→`clients`, `shop_id`→`vendor_id`, `user_id`→`client_id`, `shopName`→`vendorName`. If you find leftover `shop`, it is stale.

## Running

There are two modes, selected by the `[env]` argument to the start scripts:

### Local mode (default) — `./start-kummo.sh local`
Uses a **Supabase instance running in Docker** (managed by the Supabase CLI).
Reads credentials from `.env.local`. The start script:
1. Stops any stale Supabase containers, then runs `pnpm exec supabase start` (Docker required).
2. Runs `uv run alembic upgrade head` to create/update the `kummo` schema.
3. Starts the FastAPI backend (`fastapi dev`, hot-reload) on port 8000.

Rebuild the local DB from scratch with `uv run kummo-db-reset` (from `backend/`). It chains
`supabase db reset` → `alembic upgrade head` → seed, in that order — the order matters, because
`supabase db reset` replays only the CLI migrations and the `kummo` tables do not exist until
Alembic has run. That is also why `[db.seed] enabled = false` in `supabase/config.toml`.

### Cloud mode — `./start-kummo.sh prod`
Uses the **hosted Supabase project** (`https://xusuvidhmuyzpfrtxutd.supabase.co`).
Reads credentials from `.env.prod` and starts the FastAPI backend (`fastapi run`, no hot-reload)
on port 8000. No Docker required. Migrations are not applied automatically in this mode.

Every `.env.*` file must contain `SUPABASE_URL`, `SUPABASE_API_KEY`, `DATABASE_URL` and
`MIGRATION_DATABASE_URL` — see `backend/.env.example`.

### Manual start (either mode)
```bash
# Export credentials first
export SUPABASE_URL=... SUPABASE_API_KEY=...
export DATABASE_URL=... MIGRATION_DATABASE_URL=...

cd backend
uv run fastapi dev src/kummo/main.py   # local
uv run fastapi run src/kummo/main.py   # cloud
```
Then open `http://localhost:8000`. Do not open HTML files with `file://` — the `/api/*` routes won't resolve.

## Testing

**Backend** (from `backend/`):

- `uv run pytest -m 'not integration'` — route tests with a stubbed session; no database needed.
- `uv run pytest -m integration` — real queries against the local Supabase Postgres. Each test
  runs in a transaction that is rolled back, so seed data survives.

**Frontend** regression tests use **Vitest + jsdom** (Node dev tooling only — not needed to run the app).

- `pnpm install` once, then `pnpm test` (single run) or `pnpm run test:watch`.
- Tests live in `test/app.test.js` and cover `app.js`'s pure logic (filtering, search-URL building, card HTML, vendor enrichment, localStorage helpers) — including guards for the bugs already fixed (escaped `${}` template literals, undefined `STORAGE_*` constants).
- `app.js` is a classic browser script, so it can't be `import`ed normally. Its bottom block attaches a `globalThis.KummoApp` API (incl. a test-only `__setData(vendors, activities)` to inject fixture data). This is inert in the browser. When adding a function worth testing, add it to that export object.

## Architecture

**Pages** (each is a standalone HTML file, all sharing `js/app.js`):
- `index.html` — homepage (featured activities + search box)
- `search.html` — search/filter results, reads filters from URL query params
- `activity.html` — activity detail + booking modal (`?id=<activity-id>`)
- `profile.html` — B2C user prefs, booking history, favorites
- `business.html` — B2B dashboard; **self-contained** inline script, deliberately skipped by `app.js`. Uses a temporary vendor-selector (no auth yet); calls `GET /api/vendors`, `GET /api/activities?vendor_id=`, and `POST /api/activities`.
- `admin.html` — admin stats (business/activity/booking counts, revenue)

**`js/app.js`** is the single shared script for all B2C pages. Flow:
1. `DOMContentLoaded` → `initApp()` → `loadData()` fetches `GET /api/vendors` and `GET /api/activities` in parallel.
2. `initPage()` is a path-based router (`window.location.pathname.includes(...)`) that dispatches to the right page initializer.
3. Activities are joined to their vendor client-side via `enrichActivity()` (`activity.vendor_id === vendor.id`); the joined object exposes `vendorName` and `vendor`.

**Data sources:**
- **FastAPI backend** (`/api/*`): all reads and writes go through the backend, which holds the database and Supabase credentials server-side. No Supabase SDK in the browser.
- **`localStorage`** (client-only): bookings, favorites, and user preferences. Keys: `STORAGE_PREFS` / `STORAGE_BOOKINGS` / `STORAGE_FAVORITES`.

## Supabase setup

- Canonical project URL: `https://xusuvidhmuyzpfrtxutd.supabase.co` (20-char ref).
- Credentials live only in `.env.*` files, read by the FastAPI backend via pydantic-settings. They are never sent to the browser.
- **Supabase is used for Auth only.** Application data does not go through PostgREST: the browser never talks to Supabase and we do not use RLS, so PostgREST would be a pure HTTP hop. The backend connects to Postgres directly.
- **Two migration tools, two owners.** `supabase/migrations/` (CLI, runs as `postgres`) owns auth config, extensions and anything outside `kummo`. `backend/alembic/` (runs as `kummo_migrator`) owns every application table in the `kummo` schema. Do not create application tables from a CLI migration.
- **Two DB roles**: `kummo_migrator` for DDL (Alembic only), `kummo_app` for DML at runtime. Both are defined in `supabase/migrations/20260804155602_kummo-backend.sql`.
- Profile tables carry `auth_user_id` — unique, but no foreign key, since `auth.users` belongs to GoTrue's own role.

## Project layout

```
Kummo/
  static/
    index.html, search.html, activity.html, profile.html
    business.html, admin.html  # all pages
    js/app.js                  # shared B2C logic (calls /api/*)
    css/                       # stylesheets
  supabase/                    # Supabase CLI config, auth/extension migrations, seed.sql
    snippets/                  # one-off SQL run by hand against the hosted project
  test/                        # Vitest frontend tests
  backend/                     # FastAPI Python backend
    pyproject.toml             # uv project config; [project.scripts] holds the tasks
    .python-version            # pins Python 3.12
    .env.example               # copy to .env, fill in credentials
    alembic.ini
    alembic/                   # migrations for the kummo schema
    src/kummo/
      main.py                  # FastAPI app, mounts /api and serves static files
      config.py                # pydantic-settings Settings class
      db.py                    # async engine + get_session dependency
      orm.py                   # SQLAlchemy mappings for kummo.*
      models.py                # Pydantic request/response models
      tasks.py                 # kummo-db-seed / kummo-db-reset console scripts
      api/
        vendors.py             # GET /api/vendors
        activities.py          # GET /api/activities, GET /api/activities/{id}, POST /api/activities
    tests/                     # pytest backend tests
      integration/             # tests needing a live Postgres
```

**Running the backend** (from `backend/`):
```bash
cp .env.example .env   # fill in the four keys
uv sync --all-groups
uv run alembic upgrade head            # create/update the kummo schema
uv run fastapi dev src/kummo/main.py   # hot-reload dev server on :8000
```

## Backend conventions

- **Pydantic everywhere** — all API request bodies and response models must be typed Pydantic `BaseModel` subclasses. No raw `dict` in or out of route handlers.
- **`logging` for output** — use the standard `logging` module (`logging.getLogger(__name__)`). Never use `print()` in backend code.
- **Separate DTOs from domain types** — Pydantic models in `models.py` are the transport layer; SQLAlchemy mappings in `orm.py` are the persistence layer. Do not return ORM objects from routes.
- **Schema changes go through Alembic** — `uv run alembic revision --autogenerate -m "..."` after editing `orm.py`, then review the generated file. Never hand-edit the database.
- **`uv run` is the task runner** — no Makefile, no npm scripts, no separate task tool. Operational tasks are console scripts declared in `[project.scripts]`.
- **Test coverage** — every new route and non-trivial function requires a corresponding `pytest` test under `backend/tests/`. Use `httpx.AsyncClient` with `transport=ASGITransport(app=app)` for route tests, overriding `db.get_session`. Prefer the `StubSession` in `tests/conftest.py` for logic that does not need SQL, and `tests/integration/` for anything where the SQL itself is the thing under test.

## Frontend conventions

- No framework, no bundler — vanilla DOM APIs and template-literal HTML strings.
- `console.log` is acceptable for frontend debug output; use German for any user-facing `alert()` or rendered text.
- Supabase publishable (anon) keys are committed in `.env.*` files by design (they are public client keys); the secret service key must never appear here.
