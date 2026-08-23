# Decision records (ADRs)

Architecture Decision Records for Kummo. Each ADR captures a **settled** decision — its context, the decision itself, and the consequences. Open questions attached to a decision are gathered under [../open_questions/](../open_questions/) (business / technical) so that *what is decided* stays cleanly separated from *what is still to arbitrate*.

**Status values:** `Proposed` · `Accepted` · `Superseded` · `Deprecated`.

| # | Decision | Status | Open questions |
|---|---|---|---|
| [0001](0001-payment-stripe-connect.md) | Payment: commission via Stripe Connect | Accepted | none — fully resolved |
| [0002](0002-booking-build-vs-buy.md) | Booking platform: build in-house vs. buy | Accepted | [business/booking-build-vs-buy](../open_questions/business/booking-build-vs-buy.md) — 1 open |
| [0003](0003-persistence-sqlalchemy.md) | Persistence layer: SQLAlchemy 2.0 + Alembic | Accepted — migration strategy amended by 0004 | [technical/persistence](../open_questions/technical/persistence.md) — 1 open |
| [0004](0004-supabase-cli-single-migration-chain.md) | Schema migrations: the Supabase CLI as the single DDL chain | Accepted | — |
| [0005](0005-localization-json-catalogues.md) | Localization: English source, JSON catalogues, no library | Accepted | — |

## Not yet captured

- **Backend framework choice (FastAPI vs. alternatives)** is referenced by ADR 0003 but has no ADR of its own in this repo yet. Worth back-filling as ADR 0000 so the persistence decision has a documented parent.

## Conventions

- Filename: `NNNN-short-title.md`, zero-padded, never renumbered once merged.
- One decision per file. If a later decision reverses this one, add a new ADR and set this one's status to `Superseded`, linking both ways.
- Business-facing decisions (payment, monetization) and technical decisions both live here; the distinction is carried by content, not by folder.
