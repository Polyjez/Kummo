# Kummo — Developer Specification

| | |
|---|---|
| **Status** | Skeleton — sections marked `TODO` are not yet authored |
| **Audience** | Developers implementing the target (hand-coded) version |
| **Sources** | [../product/requirements.md](../product/requirements.md), [data-model.md](data-model.md), [sequence-diagrams/](sequence-diagrams/), [../decisions/](../decisions/) |

> **Purpose.** One buildable reference that ties together *what* to build (product requirements), *how* the data is shaped (data model), *how* flows run (sequence diagrams), and *why* the key technical choices were made (decision records). This is the document a new developer reads first. It links to the source documents rather than duplicating them; where a source is authoritative, this spec points at it.

---

## 1. Scope

The v1 target is a B2B2C marketplace for discovering and booking family/senior-friendly activities in Berlin, with commission-based monetization.

- **In scope / out of scope:** see [../product/requirements.md](../product/requirements.md) §2.
- **Actors:** Client, Vendor, Administrator, External systems — see [../product/requirements.md](../product/requirements.md) §3.
- **Functional requirements** (`FR-xx`) and **non-functional requirements** (`NFR-xx`): [../product/requirements.md](../product/requirements.md) §5–6.

> The [../product/prd.md](../product/prd.md) describes a Glide no-code MVP. Treat it as product intent; this spec describes the hand-coded target.

## 2. Architecture

Derived from [../product/requirements.md](../product/requirements.md) §7 (technical constraints).

- **Backend: Python (FastAPI).** Owns the business domain (profiles, matching engine, monetization) and exposes the application API. Chosen for maintainability/transferability (NFR-60).
- **Database & core services: Supabase** as managed PostgreSQL + Auth, Storage, Realtime. Business logic does **not** live in the database: the DB carries data integrity (constraints, transactions), the backend carries the logic.
- **Single authority for authorization:** all data access goes through the backend (NFR-41). DB-level security (RLS) is defense-in-depth, not the source of truth.
- **Frontend:** rebuilt for accessibility, DE/EN multilingualism, and mobile-first; talks to the backend API only, never directly to the DB. The existing prototype is a **UX reference**, not a code base.
- **Geodata:** PostgreSQL geospatial capabilities (PostGIS) for distances/zones; an external geocoding service converts addresses → coordinates. Zone modality pending (DEC-05, see [../open_questions/business/requirements.md](../open_questions/business/requirements.md)).
- **Persistence toolkit:** SQLAlchemy 2.0 (async) + Alembic for business-logic tables; Supabase client for Storage/Auth. See [../decisions/0003-persistence-sqlalchemy.md](../decisions/0003-persistence-sqlalchemy.md).
- **Payments:** Stripe Connect (Express), separate charges and transfers, custom booking module. See [../decisions/0001-payment-stripe-connect.md](../decisions/0001-payment-stripe-connect.md) and [../decisions/0002-booking-build-vs-buy.md](../decisions/0002-booking-build-vs-buy.md).

## 3. Data model

Authoritative source: [data-model.md](data-model.md) (conceptual ER model + settled assumptions). Open modeling choices: [../open_questions/technical/data-model.md](../open_questions/technical/data-model.md).

- **Booking state machine:** `draft → pending_payment → confirmed → completed → [transfer]`, with `cancelled_*` / `disputed` branches (see [../decisions/0001-payment-stripe-connect.md](../decisions/0001-payment-stripe-connect.md)).
- **Audit trail:** `audit_events` records payment-related domain state transitions durably, separate from technical logs.
- `TODO` — Physical schema (DDL) once open modeling decisions (OQ-DM-*) are settled.

## 4. Flows

Authoritative source: [sequence-diagrams/](sequence-diagrams/) — one diagram per use case, with a use-case coverage map in its [README](sequence-diagrams/README.md). All flows follow: frontend → Python API → Supabase; payment confirmation validated server-side.

## 5. API surface

`TODO` — Enumerate endpoints per domain (auth, profiles, activities/search, booking, payment, reviews, notifications, admin). For each: method, path, auth requirement, request/response shape, error cases. Derive the flows from [sequence-diagrams/](sequence-diagrams/). The **API contract** and the **data schema** are the durable artifacts that must survive an implementation overhaul ([../product/requirements.md](../product/requirements.md) §7).

## 6. Non-functional requirements

Authoritative source: [../product/requirements.md](../product/requirements.md) §6. Highlights for implementers:

- **Accessibility (NFR-01–03):** WCAG 2.2 AA, senior-adapted (short linear flows, explicit labels, ≥44px targets, no hover-only interactions). Structuring, designed from the outset.
- **Multilingualism (NFR-10–12):** DE/EN, i18n architecture allowing more languages; dynamic-content multilingualism pending DEC-04.
- **Mobile-first (NFR-20–21).**
- **Performance (NFR-30–31):** matching response perceived as immediate (target < 2s).
- **Security (NFR-40–42):** sensitive operations server-side; HTTPS; safe secret management.
- **Data protection (NFR-50–54):** GDPR (Berlin scope; Swiss nFADP out — see [../open_questions/business/payment.md](../open_questions/business/payment.md) OQ-PAY-6); data minimization, especially for location.
- `TODO` — Concrete acceptance criteria / test plan per NFR.

## 7. Open questions blocking the build

Consolidated from the per-document open-question files:

- **Payment (blocking):** payout timing, cancellation policy, dispute handling — [../open_questions/business/payment.md](../open_questions/business/payment.md).
- **Data model:** seats/availability, vendor↔shop cardinality, notification polymorphism — [../open_questions/technical/data-model.md](../open_questions/technical/data-model.md).
- **Product decisions:** messaging vs. contact exchange (DEC-02), dynamic-content i18n (DEC-04), service-area modality (DEC-05), engine weights (DEC-07) — [../open_questions/business/requirements.md](../open_questions/business/requirements.md).
- **Persistence:** team SQLAlchemy/Alembic conventions — [../open_questions/technical/persistence.md](../open_questions/technical/persistence.md).
