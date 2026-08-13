# Requirements — decisions to arbitrate

Open decisions from [requirements.md](../../product/requirements.md) §9. These condition the specifications and must be settled before iteration 1.

| Code | Decision | Impact | Status |
|---|---|---|---|
| **DEC-02** | After connection, do the parties exchange via **communicated contact details** or via an **internal messaging** system? | Impacts FR-73, privacy, and the v1 scope. | Open |
| **DEC-04** | Is the **dynamic content** (vendor descriptions, categories) **multilingual** (DE + EN) or German only? | A **data schema** decision to make early (costly to retrofit). | Open |
| **DEC-05** | How does a vendor define their **service area**: radius around a point, administrative zones, or a combination? | Determines the geospatial model and entry ergonomics. | Open |
| **DEC-07** | What are the **initial criteria and weights** of the matchmaking engine, beyond category / distance / availability? | Refines FR-31. | Open |
