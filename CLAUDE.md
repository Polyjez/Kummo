# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Kummo is a B2B2C web app for discovering and booking family/senior-friendly activities in Berlin. The full product vision lives in `README.md` (the PRD), which describes a *Glide* (no-code) MVP. **The actual codebase does not use Glide** — it is a hand-coded static multi-page site (plain HTML + one shared `js/app.js`) backed by **Supabase**. Treat the PRD as product intent, not as a description of the current implementation.

## Language rules

- **English** for everything developer-facing: code (identifiers, function/variable names), comments, documentation, commit messages, `console.log` debug output, and test descriptions.
- **German only for UI** — anything an end user sees: rendered page text, `alert()` messages, button labels, and the German `echo` lines in the launcher scripts.
- **Exception — DB-mapped field names stay as-is.** Fields that mirror Supabase columns keep their original spelling (`titre`, `prix`, `nom`, `adresse`, `duree`, `age_group`, `participants_max`, `disponibilites`, `type_activites`, `shop_id`). Renaming them would require a database migration. Don't "translate" these in code.
- Historical note: the code was originally French (e.g. `magasins`→`shops`, `activites`→`activities`, `enrichActivite`→`enrichActivity`); local identifiers have been migrated to English. If you find leftover French in non-DB identifiers or comments, translate it.

## Running

The app itself has no build step — it is static files that must be **served over HTTP**.

- **Do not open the HTML with `file://`** — Supabase requests fail under the `file:` protocol (the code shows a German hint telling the user to start a local server). `app.js` explicitly checks `window.location.protocol === 'file:'`.
- **Non-technical launchers** (preferred for the end user): double-click `Kummo-starten.bat` (Windows) or run `./Kummo-starten.sh` (Linux). They detect Python or Node, start a server on port 5500, and open the browser. Close the window / Ctrl+C to stop.
- **Manual**: from the repo root, `python3 -m http.server 5500` then open `http://localhost:5500`, or `npm run serve`, or VS Code Live Server.

## Testing

Regression tests use **Vitest + jsdom** (Node dev tooling only — not needed to run the app).

- `npm install` once, then `npm test` (single run) or `npm run test:watch`.
- Tests live in `test/app.test.js` and cover `app.js`'s pure logic (filtering, search-URL building, card HTML, shop enrichment, localStorage helpers) — including guards for the bugs already fixed (escaped `${}` template literals, undefined `STORAGE_*` constants).
- `app.js` is a classic browser script, so it can't be `import`ed normally. Its bottom block attaches a `globalThis.KummoApp` API (incl. a test-only `__setData(shops, activities)` to inject fixture data). This is inert in the browser. When adding a function worth testing, add it to that export object.

## Architecture

**Pages** (each is a standalone HTML file, all sharing `js/app.js`):
- `index.html` — homepage (featured activities + search box)
- `suchen.html` — search/filter results, reads filters from URL query params
- `aktivitaet.html` — activity detail + booking modal (`?id=<activity-id>`)
- `profil.html` — B2C user prefs, booking history, favorites
- `business.html` — B2B dashboard; **self-contained**, handles its own Supabase auth and CRUD inline (it is deliberately skipped by `app.js`'s router)
- `admin.html` — admin stats (business/activity/booking counts, revenue)

**`js/app.js`** is the single shared script for all the B2C pages. Flow:
1. `DOMContentLoaded` → `initApp()` checks `window.supabase` is ready → `loadData()` fetches the `shops` and `activities` tables into module-level `shops` / `activities` arrays.
2. `initPage()` is a path-based router (`window.location.pathname.includes(...)`) that dispatches to the right page initializer.
3. Activities are joined to their shop client-side via `enrichActivity()` (`activity.shop_id === shop.id`); the joined object exposes `shopName` and `shop`.

**Data sources — two separate stores:**
- **Supabase** (remote, read mostly): tables `shops` and `activities`. The Supabase client and credentials are initialized **inline in each HTML `<head>`** (see `index.html`), not in `app.js`. In `index.html`, `app.js` is injected dynamically *after* the Supabase client is confirmed ready.
- **`localStorage`** (client-only): bookings, favorites, and user preferences. Bookings are **never written back to Supabase** — `addBooking()` only persists locally, so the admin/profile booking views reflect only the current browser. Keys are defined at the top of `app.js`: `STORAGE_PREFS` / `STORAGE_BOOKINGS` / `STORAGE_FAVORITES`.

## Supabase setup

- Canonical project URL: `https://xusuvidhmuyzpfrtxutd.supabase.co` (20-char ref); the publishable (anon) key is committed in every page by design. Any page that uses data must load the supabase-js **v2** UMD SDK from the CDN **and** call `supabase.createClient(...)` into `window.supabase` *before* `js/app.js` runs. Use `supabase.createClient` (the global UMD lib), never `window.supabase.createClient`.
- Auth uses supabase-js **v2** APIs: `auth.signInWithPassword(...)` (returns `{ data: { user }, error }`) and `await auth.getUser()` (returns `{ data: { user } }`) — not v1's `auth.signIn` / `auth.user()`.
- Query tables by bare name: `.from('shops')`, `.from('activities')` — not `.from('public.shops')`.
- CORS was an open problem per commit history; if requests fail, check the project's allowed origins.

## Conventions

- No framework, no bundler — vanilla DOM APIs and template-literal HTML strings.
- Supabase publishable (anon) keys are committed in the HTML by design (they are public client keys); the secret service key must never appear here.
