# Requirements — decisions to arbitrate

Open decisions from [requirements.md](../../product/requirements.md) §9. These condition the specifications and must be settled before iteration 1.

> **Note on status.** This requirements document is the earlier "matchmaking / connection" framing (v0.1). Several of its decisions have since been settled by the decision records under [../decisions/](../../decisions/), which supersede the connection-only monetization model. Status below reflects that.

| Code | Decision | Impact | Status |
|---|---|---|---|
| **DEC-01** | Does the payment for the final service between client and vendor **transit through the platform**, or does the platform only bill the connection? | Determines the extent of transactional needs and part of the architecture. | **Resolved** → payment transits through the platform. See [ADR 0001](../../decisions/0001-payment-stripe-connect.md). |
| **DEC-02** | After connection, do the parties exchange via **communicated contact details** or via an **internal messaging** system? | Impacts FR-73, privacy, and the v1 scope. | Open |
| **DEC-03** | Which **monetization model** (§4): pay-per-lead, contact unlock, subscription, success commission, or a combination? | Conditions all of section 5.6. | **Resolved** → percentage **success commission** on the client's payment. See [ADR 0001](../../decisions/0001-payment-stripe-connect.md). |
| **DEC-04** | Is the **dynamic content** (vendor descriptions, categories) **multilingual** (DE + EN) or German only? | A **data schema** decision to make early (costly to retrofit). | Open |
| **DEC-05** | How does a vendor define their **service area**: radius around a point, administrative zones, or a combination? | Determines the geospatial model and entry ergonomics. | Open |
| **DEC-06** | Which **regulatory scope**: Switzerland only (nFADP), or also EU users (GDPR)? | Impacts the compliance requirements (§6.6). | **Resolved** → Berlin-only scope, GDPR only, no Swiss nexus. See [ADR 0001](../../decisions/0001-payment-stripe-connect.md) (OQ-PAY-6). |
| **DEC-07** | What are the **initial criteria and weights** of the matchmaking engine, beyond category / distance / availability? | Refines FR-31. | Open |
