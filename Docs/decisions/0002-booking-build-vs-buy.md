# ADR 0002 — Booking platform: build in-house vs. buy

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-07 |
| **Deciders** | Business owner, tech lead |
| **Depends on** | [ADR 0001 — Payment: commission via Stripe Connect](0001-payment-stripe-connect.md) |
| **Open questions** | [open_questions/business/booking-build-vs-buy.md](../open_questions/business/booking-build-vs-buy.md) |

## Context

Kummo's payment model ([ADR 0001](0001-payment-stripe-connect.md)) is a **percentage commission on the client's payment**, processed via **Stripe Connect** (separate charges and transfers), with a deferred vendor payout window and a durable audit trail (`audit_events`). The booking module must fit this model, not the other way around. Two categories of existing solutions were evaluated against this requirement.

### Option A — Generic scheduling tools (e.g. Cal.com, Calendly)

Built for one-to-one or team meeting scheduling, not a two-sided activity marketplace.

- Cal.com's core is open source, but commercial self-hosting now requires a paid license key — no longer unconditionally free in production.
- Stripe support exists only for simple per-event-type payment — no native concept of a third-party vendor, KYC onboarding, or commission split.
- No concept of geographic matching, multi-vendor payout, or a business-level audit trail.

**Assessment:** structural mismatch. These are shared calendars, not marketplaces.

### Option B — Vertical "tour & activity" booking SaaS (e.g. Bokun, FareHarbor, Regiondo)

Domain-closer (activity booking + payment + commission), but each **is itself the merchant of record** and imposes its own payment/commission engine.

- Pricing is commission-based and material at scale: Bokun $49/mo + 1.5% to $499/mo + 1%; FareHarbor up to 2% on API bookings and up to 6% on direct; Regiondo 3% on gross revenue despite "no commission" marketing.
- Adopting one would re-platform Kummo's monetization onto *their* split and payout logic — in direct conflict with the Stripe Connect architecture and audit trail already defined.
- The market has consolidated heavily (Rezdy-Checkfront-Regiondo merger; FareHarbor owned by Booking Holdings; Bokun owned by Tripadvisor), increasing long-term roadmap dependency risk.
- Designed for individual tour operators distributing through OTAs (Viator, GetYourGuide) — not a white-labeled, senior-first marketplace Kummo owns end-to-end.

**Assessment:** business-model mismatch. Using one would make Kummo a tenant of a third party's commission engine rather than the owner of its own.

### Option C — Dedicated implementation (FastAPI, as currently architected)

The actual booking logic required for v1 is narrow: an activity availability model plus a booking state machine (`draft → pending_payment → confirmed → completed → transfer`, with `cancelled_*` / `disputed` branches). The complex, regulated part — KYC, funds transmission, payout — is already delegated to Stripe Connect Express, which is provider-agnostic and does not require a third-party booking SaaS on top.

## Decision

Build a **dedicated booking module** within the existing FastAPI/Supabase/Stripe Connect architecture, rather than adopting a third-party scheduling tool or vertical booking SaaS.

Neither external option fit: generic scheduling tools do not support a commissioned marketplace model, and vertical booking SaaS platforms would require ceding the payment/commission architecture already validated for Kummo. A third-party tool would only be worth revisiting if the availability model grows into complex multi-resource, multi-location scheduling — out of scope for v1.

## Consequences

- Full ownership of the commission model, matching criteria, and audit trail, consistent with [ADR 0001](0001-payment-stripe-connect.md).
- No recurring per-booking fee layered on top of Stripe Connect's own costs; no vendor lock-in to a consolidating SaaS market.
- Maintainable by Python developers post-handoff, as required.
- **Trade-off:** Kummo's team builds and maintains the booking state machine and availability logic itself, rather than inheriting it from a mature product. Given the scope (single city, deterministic matching, no complex multi-resource calendars), this is assessed as a modest, well-bounded effort.
