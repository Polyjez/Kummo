# Payment — open questions

Open decisions attached to [ADR 0001 — Payment: commission via Stripe Connect](../../decisions/0001-payment-stripe-connect.md). These require **business validation** before the payment module is finalized; they have direct impact on vendor cash flow, legal/compliance scope, and platform revenue assurance, and should be validated explicitly rather than left to technical defaults.

**Blocking for the payment module:** OQ-PAY-1, OQ-PAY-2, OQ-PAY-3.
**Configuration / UX (non-blocking for the initial build):** OQ-PAY-4, OQ-PAY-5, OQ-PAY-7.

| # | Question | Impact | Status |
|---|---|---|---|
| OQ-PAY-1 | **Payout timing window.** After an activity is marked `completed`, how long should Kummo wait before transferring the vendor's share? | Directly affects vendor cash flow (a long window may discourage adoption) and Kummo's exposure to late cancellations/disputes (a short window risks paying out before a refund is needed). A default candidate (e.g. J+2) has been proposed technically but **not** validated as a business rule. | Open — blocking |
| OQ-PAY-2 | **Cancellation policy.** Rules for client-initiated cancellations (full / partial / time-based tiers) and vendor-initiated cancellations (always a full automatic refund?). | Must be defined before refund logic can be implemented; must be communicated clearly at booking time (senior-friendly, unambiguous wording). | Open — blocking |
| OQ-PAY-3 | **Dispute handling process.** When a client or vendor disputes that an activity took place as booked, who resolves it (manual admin action) and what outcomes are possible (release payout / refund client / partial split)? | Defines the admin tooling scope for v1 and the SLA expectations set with vendors. | Open — blocking |
| OQ-PAY-4 | **Commission rate structure.** Single flat percentage across all activities, or varying by activity type, vendor tier, or price bracket? | Determines whether the commission rate is a single config value or a per-vendor/per-activity attribute in the data model (see [../technical/data-model.md](../technical/data-model.md)). | Open |
| OQ-PAY-5 | **Failed vendor payouts.** If a vendor's Stripe account is not fully onboarded (KYC incomplete) or a transfer fails, should the platform hold the booking, allow it and retry later, or block new bookings for that vendor? | Affects vendor onboarding UX and whether payout readiness is a booking prerequisite. | Open |
| OQ-PAY-6 | **Currency and scope.** | Platform scoped to **Berlin only**, no operational link to Switzerland. **EUR only** for v1; no multi-currency. Removes Swiss nLPD from compliance scope — GDPR alone applies, assuming no Swiss nexus. | **Resolved** |
| OQ-PAY-7 | **Client-facing transparency.** Should clients see the commission amount separately at checkout (transparent pricing) or only the total price (commission absorbed)? | Legal/trust consideration, particularly relevant for a senior-facing product where clarity and trust are core UX requirements. | Open |
