# ADR 0001 — Payment: commission via Stripe Connect

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-07 |
| **Deciders** | Business owner, tech lead |
| **Supersedes** | The "connection-only" monetization framing and the pay-per-lead options in [../product/requirements.md](../product/requirements.md) §4 (see DEC-01, DEC-03) |
| **Open questions** | [open_questions/business/payment.md](../open_questions/business/payment.md) |

## Context

Kummo's revenue model is a **percentage commission on the amount paid by the client** for a booked activity — not a flat lead-generation fee.

Because the commission is a percentage of the actual transaction, **relying on the vendor to self-report the transaction amount (periodic invoicing) is not viable**: it cannot be technically verified and creates a structural risk of under-reporting. Consequently, **Kummo must process the client's payment directly** rather than only facilitating the introduction. This is a shift from the platform's original "connection-only" monetization framing, driven purely by the commission model.

## Decision

- Payment is implemented via **Stripe Connect**, using the *separate charges and transfers* pattern: the client's payment is received on Kummo's Stripe account first; the vendor's share is transferred to them afterward, once Kummo triggers it.
- Vendor accounts use **Stripe Connect Express** (Stripe-hosted KYC/onboarding). This is not primarily a UX choice: as soon as Kummo receives client funds and forwards a share to a third party (the vendor), Kummo performs a regulated payment/funds-transmission activity (PSD2 scope). Connect delegates that regulatory burden to Stripe, which holds the transiting funds and executes the payout under its own license. The vendor's only interaction is a one-time hosted form (identity, IBAN) — no dashboard, no ongoing technical involvement.
- The commission is **retained on Kummo's account by construction** — it never needs to be actively "collected" after the fact, removing the collection-risk of the invoicing model.

### Technical approach

- `bookings` follow a state machine: `draft → pending_payment → confirmed → completed → [transfer triggered]`, with `cancelled_*` and `disputed` branches.
- The vendor payout (`transfer`) is **not** triggered immediately at payment. It is deferred by a safety window after the activity's scheduled date, to allow cancellations or disputes to be resolved without needing to reverse a completed transfer.
- All payment-related state transitions are recorded as durable domain events (`audit_events`), separate from technical/observability logs.

## Consequences

- Kummo is the merchant of record for the client's payment; the booking module is built around the Stripe Connect flow, not the other way around (this constraint drives [ADR 0002](0002-booking-build-vs-buy.md)).
- Regulatory burden (KYC, funds transmission) is delegated to Stripe; Kummo does not hold a payment license.
- Several business rules (payout window, cancellation/refund policy, dispute handling) must be settled before the payment module can ship — tracked as open questions.
- Scope is **EUR only, Berlin only** (see open question OQ-PAY-6, resolved): GDPR alone applies, Swiss nFADP is out of scope, no multi-currency handling.
