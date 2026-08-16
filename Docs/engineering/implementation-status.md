# Implementation status

| | |
|---|---|
| **Purpose** | The delta between the target described in [specification.md](specification.md) and the code that exists today |
| **Reflects** | branch `feature/python-backend`, 16 August 2026 |
| **Audience** | Developers picking up the next piece of work |

> **How this document relates to the others.** [specification.md](specification.md) and
> [../product/requirements.md](../product/requirements.md) describe the **target**; they do not
> change as code lands. This page is the only place that describes **what runs today**. If the two
> disagree, this page is wrong and should be corrected — never the other way round.

Legend: **Built** — implemented and reachable end-to-end · **Partial** — a usable subset, gaps
named · **Not started** — no code.

---

## 1. Areas at a glance

| Area | Status | Where |
|---|---|---|
| Authentication & sessions | **Built** | `backend/src/kummo/auth/`, `static/js/auth.js` |
| Vendor & client profiles | **Partial** | `vendors/`, `clients/` |
| Activity catalogue | **Partial** | `activities/` |
| Discovery: browse, search, filter | **Partial** (client-side) | `static/js/app.js` |
| Booking | **Partial** (localStorage only) | `static/js/app.js`, `activity.html` |
| Payment / commission | **Not started** | — |
| Matching engine & geodata | **Not started** | — |
| Reviews | **Not started** | — |
| Notifications | **Not started** | — |
| Administration | **Partial** (read-only, client-side) | `static/admin.html`, `app.js` |
| Accessibility, i18n (DE/EN) | **Not started** | — |

## 2. What is built

**Authentication** is the one area implemented to the target architecture. Layered
outermost-first (`routes` → `dependencies` → `profiles` → `cookies` → `tokens` → `service`), with
`service.py` the only module that knows the provider is Supabase.

- `POST /api/auth/register/client`, `/register/vendor`, `/login`, `/logout`, `/refresh`,
  `GET /api/auth/me`, `GET /api/auth/oauth/{provider}`, `GET /api/auth/callback`.
- Session transport is two HttpOnly cookies (`kummo_session`, `kummo_refresh`). No token ever
  reaches page JS.
- Google OAuth uses PKCE, verifier in a short-lived HttpOnly cookie. **OAuth signup always
  creates a client** — a vendor needs an address and activity types a Google profile cannot supply.
- Role routing: `client.html` and `vendor.html` are the two role homes, each guarded by
  `KummoAuth.requireUser(role)`.
- Registration is deliberately **not atomic** (identity over HTTP, profile row in a local
  transaction). Every entry path calls `ensure_*_profile`, so an interrupted registration
  completes on the next sign-in. See [ADR 0004](../decisions/0004-supabase-cli-single-migration-chain.md)
  for the surrounding migration model.

Covers FR-01, FR-05, and the [authentication flow](sequence-diagrams/00-authentication.md).

**Persisted schema** — three tables in the `kummo` schema, owned by
`supabase/migrations/` and guarded by
`backend/tests/integration/test_schema_matches_data_model.py`:

| Table | Columns |
|---|---|
| `vendors` | `id`, `created_at`, `auth_user_id`, `name`, `address`, `phone`, `email`, `website`, `activity_type[]`, `picture` |
| `clients` | `id`, `created_at`, `auth_user_id`, `first_name`, `last_name`, `email`, `age`, `interests[]`, `number_children` |
| `activities` | `id`, `created_at`, `vendor_id`, `title`, `description`, `price`, `participants_max`, `duration`, `age_group`, `picture` |

**Read/write API** — `GET /api/vendors`, `GET /api/activities` (optional `vendor_id` filter),
`GET /api/activities/{id}`, `POST /api/activities`.

## 3. What remains

Ordered roughly by what unblocks the most.

### 3.1 Sessions and availability — blocks booking, payment, search

There is **no session/availability concept in the schema at all**. `activities` carries
`participants_max` and `duration` but no dates and no seat count; the `disponibilites` column the
old code referenced never existed, and the availability field on `vendor.html` is deliberately not
persisted, pending the modeling decision in
[open_questions/technical/data-model.md](../open_questions/technical/data-model.md) (counter on
`SESSION` vs. derived from bookings).

Everything below depends on this. **Settle OQ-DM first.**

Missing: FR-15 (add/disable/update a session), FR-60's availability filter.

### 3.2 Booking

Bookings exist only as `localStorage` entries under `kummo_bookings`, written by the modal in
`activity.html`. Nothing reaches the server, so a booking is invisible to the vendor and lost on
another device.

Missing: the `bookings` table, the state machine
(`draft → pending_payment → confirmed → completed`, with `cancelled_*` / `disputed` branches),
the booking API, and the vendor-side view. See
[02-book-and-pay](sequence-diagrams/02-book-and-pay.md),
[03-change-booking](sequence-diagrams/03-change-booking.md),
[08-vendor-cancel-reschedule](sequence-diagrams/08-vendor-cancel-reschedule.md).

### 3.3 Payment and commission — FR-50…53

Nothing. No Stripe dependency, no `audit_events` table. The design is settled in
[ADR 0001](../decisions/0001-payment-stripe-connect.md) (Stripe Connect Express, separate charges
and transfers) and [ADR 0002](../decisions/0002-booking-build-vs-buy.md) (custom booking module),
but **three business questions block the build**: payout timing, cancellation policy and dispute
handling — [open_questions/business/payment.md](../open_questions/business/payment.md).

### 3.4 Matching engine and geodata — FR-30…36, FR-40…45

Nothing. No PostGIS, no geocoding, no coordinates on `vendors` (only a free-text `address`), no
service-area model, no score. `app.js` does a substring match over the activity list in the
browser instead.

Blocked on DEC-05 (service-area modality: radius vs. administrative zones) and DEC-07 (engine
weights) — [open_questions/business/requirements.md](../open_questions/business/requirements.md).

### 3.5 Server-side search — FR-60, FR-61

`app.js` fetches the **entire** vendor and activity list on every page load and filters in the
browser (`filterActivities`, `enrichActivity` joins `activity.vendor_id === vendor.id`
client-side). Correct for a seeded catalogue, not for a real one, and it cannot support FR-61
(search by area) without 3.4.

### 3.6 Profile management — FR-03, FR-04

`GET /api/auth/me` returns name and email read-only. There is no route to edit a profile and none
to delete an account, so the right to erasure (NFR-50…54) is unimplemented. There is no
`preferred_language` column, so FR-04 and FR-72 have nowhere to read from.

Client preferences and favourites live in `localStorage` (`kummo_prefs`, `kummo_favorites`),
scoped to the signed-in account id via `kummo_account`.

### 3.7 Reviews, notifications, support, sharing

Not started: FR-70…73 (notifications), and the flows in
[05-review](sequence-diagrams/05-review.md), [09-reminder](sequence-diagrams/09-reminder.md),
[10-support](sequence-diagrams/10-support.md),
[11-share-booking](sequence-diagrams/11-share-booking.md). FR-73 (contact exchange vs. internal
messaging) is still open as DEC-02.

### 3.8 Administration — FR-80…83

`admin.html` renders counts and revenue computed in the browser from the public activity list plus
whatever bookings happen to be in that browser's `localStorage` — the figures are per-device, not
platform-wide. There is no admin role, no admin API, no moderation, no category/weight
configuration.

### 3.9 Non-functional

None of the structuring NFRs are addressed yet, and two of them
(accessibility, i18n) are the kind that get much more expensive after the fact:

- **Accessibility (NFR-01…03)** — WCAG 2.2 AA, senior-adapted. Not audited.
- **Multilingualism (NFR-10…12)** — UI text is hard-coded German. No i18n layer.
  Dynamic-content multilingualism is still open as DEC-04.
- **Performance (NFR-30…31)** — no measurement; 3.5 works against it.
- **Email verification** — `enable_confirmations = false` in `supabase/config.toml`, and there is
  no password-reset route. FR-02 is therefore only half met.

## 4. Deviations from the specification

Places where the code intentionally differs from [specification.md](specification.md):

| Spec says | Code does | Why |
|---|---|---|
| Supabase as "managed PostgreSQL + Auth, Storage, Realtime" | Auth only; Postgres accessed directly | The browser never talks to Supabase and we do not use RLS, so PostgREST would be a pure HTTP hop |
| Persistence: "SQLAlchemy 2.0 + Alembic" ([ADR 0003](../decisions/0003-persistence-sqlalchemy.md)) | SQLAlchemy 2.0; Alembic removed | Superseded by [ADR 0004](../decisions/0004-supabase-cli-single-migration-chain.md) — the Supabase CLI is the single DDL chain |
| "Frontend rebuilt for accessibility, DE/EN, mobile-first" | The prototype is still the running frontend | Not yet started; see 3.9 |
| "RLS is defense-in-depth" | No RLS | One DML-only role (`kummo_app`); all access goes through the backend |
