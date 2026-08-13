# ADR 0001 — Payment: commission via Stripe Connect

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-07 |
| **Deciders** | Business owner, tech lead |
| **Supersedes** | The "connection-only" monetization framing and the pay-per-lead options in [../product/requirements.md](../product/requirements.md) §4 (see DEC-01, DEC-03) |
| **Open questions** | None — all resolved, see Business rules below |

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

### Business rules (resolved OQ-PAY-1, -2, -3, -4, -5, -7)

- **Payout window:** the vendor is paid 48h after the activity has successfully taken place.
- **Cancellation policy:** vendor-initiated cancellations are refunded to the client in full via Kummo. Client-initiated cancellations are refunded in full if made more than 48h before the activity start, and not refunded otherwise. The vendor contract should include a clause giving Kummo flexibility to act if a vendor cancels excessively.
- **Dispute handling (MVP):** disputes are resolved manually, case by case. Outcomes are limited to a full refund to the client, or withholding the payout to the vendor. A more systematic process may be defined post-MVP.
- **Commission rate:** flat 15% across all activities (no per-vendor/per-activity variation for v1).
- **Checkout transparency:** clients see only the total price; the commission is absorbed and not itemized separately.
- **Vendor onboarding / payout readiness:** every vendor is **required to complete a Stripe Connect Express account** (identity + IBAN, Stripe-hosted) as part of becoming a vendor on Kummo — confirming the architecture above and resolving the earlier ambiguity about whether vendors need their own Stripe account. A vendor with incomplete KYC cannot receive payouts, so Express onboarding is effectively a prerequisite of vendor activation, not a per-booking check; any transfer failure for an already-onboarded vendor is handled through the manual dispute process (OQ-PAY-3) for the MVP.
  - **Cost:** under Stripe's platform-priced model, each active Express account (one that received a payout that period) costs Kummo **€2/month**, plus **0.25% + €0.10 per payout** to the vendor's bank (higher for cross-border payouts, or +1% for instant payouts). The internal transfer from Kummo's balance to the vendor's Connect balance carries no separate Stripe fee — the cost is only incurred at the payout-to-bank step. This is on top of the standard EU card processing fee (1.5% + €0.25) Stripe charges Kummo on the client's original payment.

## Consequences

- Kummo is the merchant of record for the client's payment; the booking module is built around the Stripe Connect flow, not the other way around (this constraint drives [ADR 0002](0002-booking-build-vs-buy.md)).
- Regulatory burden (KYC, funds transmission) is delegated to Stripe; Kummo does not hold a payment license.
- Payout window, cancellation/refund policy, dispute handling, commission rate, vendor onboarding, and checkout transparency are all settled (above).
- Scope is **EUR only, Berlin only** (see open question OQ-PAY-6, resolved): GDPR applies, no multi-currency handling.
