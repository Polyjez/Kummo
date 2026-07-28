# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Kummo is a B2B2C web app for discovering and booking family/senior-friendly activities in Berlin. The full product vision lives in `README.md` (the PRD), which describes a *Glide* (no-code) MVP. **The actual codebase does not use Glide** — it is a static multi-page site (`static/`) served by a **FastAPI** backend (`backend/`) backed by **Supabase**. Treat the PRD as product intent, not as a description of the current implementation.

## Language rules

- **English** for everything developer-facing: code (identifiers, function/variable names), comments, documentation, commit messages, `console.log` debug output, and test descriptions.
- **German only for UI** — anything an end user sees: rendered page text, `alert()` messages, button labels, and the German `echo` lines in the launcher scripts.
- **DB-mapped field names mirror Supabase columns** (see `schema.sql`): `title`, `price`, `name`, `address`, `duration`, `picture`, `activity_type`, `age_group`, `participants_max`, `shop_id`, etc. These are now English to match the actual columns — keep them spelled exactly as the column. There is **no `disponibilites`/availability column** in the schema; code that referenced it is guarded as optional, and the availability form field on `business.html` is not persisted (pending a product/schema decision).
- Historical note: the code (and originally the DB columns) was French — `titre`→`title`, `prix`→`price`, `nom`→`name`, `adresse`→`address`, `duree`→`duration`, `photo`→`picture`, `type_activites`→`activity_type` (and earlier `magasins`→`shops`, `activites`→`activities`). All identifiers are now English. If you find leftover French, translate it.

## Running

There are two modes, selected by the `[env]` argument to the start scripts:

### Local mode (default) — `./start-kummo.sh local`
Uses a **Supabase instance running in Docker** (managed by the Supabase CLI).
Reads credentials from `.env.local`. The start script:
1. Stops any stale Supabase containers, then runs `npx supabase start` (Docker required).
2. Patches `static/js/config.js` with the local Supabase URL + anon key (used by `business.html`).
3. Starts the FastAPI backend (`fastapi dev`, hot-reload) on port 8000.

Seed data lives in `supabase/seed.sql`; schema migrations in `supabase/migrations/`.
Reset the local DB with `npx supabase db reset` from the repo root.

### Cloud mode — `./start-kummo.sh cloud`
Uses the **hosted Supabase project** (`https://xusuvidhmuyzpfrtxutd.supabase.co`).
Reads credentials from `.env.cloud`. The start script:
1. Patches `static/js/config.js` with the remote Supabase URL + anon key (used by `business.html`).
2. Starts the FastAPI backend (`fastapi run`, no hot-reload) on port 8000.

No Docker required. The `.env.cloud` file must contain `SUPABASE_URL` and `SUPABASE_ANON_KEY`.

### Manual start (either mode)
```bash
# Export credentials first
export SUPABASE_URL=...
export SUPABASE_ANON_KEY=...

cd backend
uv run fastapi dev src/kummo/main.py   # local
uv run fastapi run src/kummo/main.py   # cloud
```
Then open `http://localhost:8000`. Do not open HTML files with `file://` — the `/api/*` routes won't resolve.

## Testing

Regression tests use **Vitest + jsdom** (Node dev tooling only — not needed to run the app).

- `npm install` once, then `npm test` (single run) or `npm run test:watch`.
- Tests live in `test/app.test.js` and cover `app.js`'s pure logic (filtering, search-URL building, card HTML, shop enrichment, localStorage helpers) — including guards for the bugs already fixed (escaped `${}` template literals, undefined `STORAGE_*` constants).
- `app.js` is a classic browser script, so it can't be `import`ed normally. Its bottom block attaches a `globalThis.KummoApp` API (incl. a test-only `__setData(shops, activities)` to inject fixture data). This is inert in the browser. When adding a function worth testing, add it to that export object.

## Architecture

**Pages** (each is a standalone HTML file, all sharing `js/app.js`):
- `index.html` — homepage (featured activities + search box)
- `search.html` — search/filter results, reads filters from URL query params
- `activity.html` — activity detail + booking modal (`?id=<activity-id>`)
- `profile.html` — B2C user prefs, booking history, favorites
- `business.html` — B2B dashboard; **self-contained** inline script, deliberately skipped by `app.js`. Uses a temporary shop-selector (no auth yet); calls `GET /api/shops`, `GET /api/activities?shop_id=`, and `POST /api/activities`.
- `admin.html` — admin stats (business/activity/booking counts, revenue)

**`js/app.js`** is the single shared script for all B2C pages. Flow:
1. `DOMContentLoaded` → `initApp()` → `loadData()` fetches `GET /api/shops` and `GET /api/activities` in parallel.
2. `initPage()` is a path-based router (`window.location.pathname.includes(...)`) that dispatches to the right page initializer.
3. Activities are joined to their shop client-side via `enrichActivity()` (`activity.shop_id === shop.id`); the joined object exposes `shopName` and `shop`.

**Data sources:**
- **FastAPI backend** (`/api/*`): all reads and writes go through the backend, which holds the Supabase credentials server-side. No Supabase SDK in the browser.
- **`localStorage`** (client-only): bookings, favorites, and user preferences. Keys: `STORAGE_PREFS` / `STORAGE_BOOKINGS` / `STORAGE_FAVORITES`.

## Supabase setup

- Canonical project URL: `https://xusuvidhmuyzpfrtxutd.supabase.co` (20-char ref).
- Credentials (`SUPABASE_URL`, `SUPABASE_ANON_KEY`) live only in `.env.*` files, read by the FastAPI backend at startup via pydantic-settings. They are never sent to the browser.
- The backend uses the **anon key** (subject to RLS). Switch to the service role key once RLS policies are defined and auth is wired up.
- Local DB: managed by `npx supabase` (Docker). Schema migrations in `supabase/migrations/`, seed data in `supabase/seed.sql`.

## Project layout

```
Kummo/
  static/
    index.html, search.html, activity.html, profile.html
    business.html, admin.html  # all pages
    js/app.js                  # shared B2C logic (calls /api/*)
    css/                       # stylesheets
  supabase/                    # local Supabase config + migrations
  test/                        # Vitest frontend tests
  backend/                     # FastAPI Python backend
    pyproject.toml             # uv project config
    .python-version            # pins Python 3.12
    .env.example               # copy to .env, fill in credentials
    src/kummo/
      main.py                  # FastAPI app, mounts /api and serves static files
      config.py                # pydantic-settings Settings class
      db.py                    # Supabase client factory
      models.py                # Pydantic response models
      api/
        shops.py               # GET /api/shops
        activities.py          # GET /api/activities, GET /api/activities/{id}, POST /api/activities
    tests/                     # pytest backend tests
```

**Running the backend** (from `backend/`):
```bash
cp .env.example .env   # fill in SUPABASE_URL + SUPABASE_ANON_KEY
uv sync --all-groups
uv run fastapi dev src/kummo/main.py   # hot-reload dev server on :8000
```

## Backend conventions

- **Pydantic everywhere** — all API request bodies and response models must be typed Pydantic `BaseModel` subclasses. No raw `dict` in or out of route handlers.
- **`logging` for output** — use the standard `logging` module (`logging.getLogger(__name__)`). Never use `print()` in backend code.
- **Test coverage** — every new route and non-trivial function requires a corresponding `pytest` test under `backend/tests/`. Use `httpx.AsyncClient` with `transport=ASGITransport(app=app)` for route tests. Mock Supabase at the `db.get_supabase` boundary.

## Frontend conventions

- No framework, no bundler — vanilla DOM APIs and template-literal HTML strings.
- `console.log` is acceptable for frontend debug output; use German for any user-facing `alert()` or rendered text.
- Supabase publishable (anon) keys are committed in `.env.*` files by design (they are public client keys); the secret service key must never appear here.
