# Kummo — Documentation

Documentation for Kummo, a B2B2C platform for discovering and booking family/senior-friendly activities in Berlin. This folder is organized along two axes: **business vs. technical**, and **settled decisions vs. open questions**.

```
Docs/
├── product/         Business — the "what" (validated by the product owner)
├── engineering/     Technical — the "how" (for developers)
├── decisions/       ADRs — settled decisions
├── open_questions/  What is still to arbitrate — split business / technical
└── archive/         Superseded / reference-only material
```

## Where to start

| You are… | Start here |
|---|---|
| A **developer** implementing the target version | [engineering/specification.md](engineering/specification.md), then [engineering/](engineering/) |
| A **product owner** validating the need | [product/requirements.md](product/requirements.md) |
| Looking for **why a technical/business choice was made** | [decisions/](decisions/) |
| Looking for **what is still undecided** | [open_questions/](open_questions/) (business / technical) |

## Business — [product/](product/)

| Document | What it is |
|---|---|
| [product/requirements.md](product/requirements.md) | Functional & non-functional requirements (canonical, EN). §9 open decisions in [open_questions/business/requirements.md](open_questions/business/requirements.md). |
| [product/brainstorming.md](product/brainstorming.md) | Early feature brainstorming and use-case list (historical). |

## Technical — [engineering/](engineering/)

| Document | What it is |
|---|---|
| [engineering/specification.md](engineering/specification.md) | Consolidated developer specification (entry point; some sections `TODO`). |
| [engineering/data-model.md](engineering/data-model.md) | Conceptual ER model + settled assumptions. |
| [engineering/sequence-diagrams/](engineering/sequence-diagrams/) | Use-case flow diagrams (frontend → API → Supabase). |

## Decisions (ADRs) — [decisions/](decisions/)

Each ADR is a **settled** decision; its open points are gathered under [open_questions/](open_questions/). See the [ADR index](decisions/README.md).

| # | Decision |
|---|---|
| [0001](decisions/0001-payment-stripe-connect.md) | Payment: commission via Stripe Connect |
| [0002](decisions/0002-booking-build-vs-buy.md) | Booking platform: build in-house vs. buy |
| [0003](decisions/0003-persistence-sqlalchemy.md) | Persistence layer: SQLAlchemy 2.0 + Alembic |

## Open questions — [open_questions/](open_questions/)

All open questions are gathered here, split by audience. See the [open-questions index](open_questions/README.md).

**Business** — [open_questions/business/](open_questions/business/)
- [payment.md](open_questions/business/payment.md) — payout timing, cancellation, disputes, commission structure… (3 blocking)
- [booking-build-vs-buy.md](open_questions/business/booking-build-vs-buy.md) — in-house maintenance trade-off
- [requirements.md](open_questions/business/requirements.md) — DEC-01…07 (several now resolved by ADR 0001)

**Technical** — [open_questions/technical/](open_questions/technical/)
- [data-model.md](open_questions/technical/data-model.md) — seats/availability, vendor↔shop, notifications
- [persistence.md](open_questions/technical/persistence.md) — team SQLAlchemy/Alembic conventions

## Archive — [archive/](archive/)

Superseded or reference-only. [prd-glide-mvp.md](archive/prd-glide-mvp.md) is the original Glide-aligned PRD (v2.0), superseded by the ADRs (business model, booking, stack); [requirements.fr.md](archive/requirements.fr.md) is the original French cahier des charges (the English [product/requirements.md](product/requirements.md) is now canonical); [cahier-des-charges-artifact-url.md](archive/cahier-des-charges-artifact-url.md) is a link to an external artifact.
