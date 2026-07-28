# Matchmaking Platform Requirements

| | |
|---|---|
| **Version** | 0.1 — draft pending approval |
| **Date** | 2 July 2026 |
| **Status** | To be approved by the product owner |
| **Recipient** | Product owner |
| **Purpose** | Frame the functional need and project constraints, ahead of detailed specifications and iteration breakdown |

> **How to read this document.** Sections 1 to 6 describe the *need* (the "what") in business language: this is what the product owner approves. Section 7 gathers the *technical constraints* (the "how"), which will be detailed later in the specifications. Section 8 proposes an iteration breakdown. Section 9 lists the **decisions to arbitrate** before moving to specifications: these are the blocking points.

---

## 1. Context and objectives

The platform connects two populations: **clients** expressing a need and **vendors / service providers** offering an offer. Kummo's role is to **connect** the two and facilitate the booking; its revenue is a **percentage commission on the client's payment** for a booked activity (see §4 and [ADR 0001](../decisions/0001-payment-stripe-connect.md)), not the sale of the vendors' own products or services.

The matchmaking engine relies on the characteristics of both parties, including **geographic proximity**, which is a decisive criterion.

An initial visual prototype was produced (static interface, without robust business logic). It serves as a **reference mockup for the user experience**, but **not as a technical foundation** for the target version.

**Project objectives:**

- **OBJ-01** — Allow a client to express a need and obtain a list of relevant vendors, ordered by suitability.
- **OBJ-02** — Allow a vendor to present their offer and service area, and receive qualified connections.
- **OBJ-03** — Monetize via a **percentage commission** on the client's payment (see §4, [ADR 0001](../decisions/0001-payment-stripe-connect.md)).
- **OBJ-04** — Offer an accessible experience, mobile-first, adapted to a senior audience.
- **OBJ-05** — Offer the service in German and English.

---

## 2. Scope

### 2.1 In scope

- Account and profile management for both populations (client / vendor).
- Entry and management of the vendor offer, including the geographic service area.
- Expression of the client's need.
- Multi-criteria matchmaking engine including distance.
- Commission-based monetization on payments processed through the platform (§4).
- Notifications to the parties.
- Administration and moderation back-office.
- Usage tracking (usage statistics, basis for future engine evolutions).
- Multilingual (DE/EN), accessible, mobile-first interface.

### 2.2 Out of scope (at least for the first version)

- **OUT-02** — Advanced recommendation engine using machine learning (the v1 engine is a deterministic multi-criteria scoring; learning is a later evolution).
- **OUT-03** — Native mobile application (responsive mobile web covers the initial need).
- **OUT-04** — Rich real-time internal messaging between client and vendor (to be confirmed depending on the connection model, DEC-02).

### 2.3 Structuring assumptions

- **ASM-01** — The target audience includes a significant proportion of seniors; ergonomics and accessibility are first-order requirements, not options.
- **ASM-02** — Usage will occur mostly on mobile phones.
- **ASM-03** — The interface content is initially in German; English is required.

---

## 3. Actors

| Code | Actor | Description |
|---|---|---|
| **A-CLI** | Client | Expresses a need, reviews the proposed vendors, initiates a connection. |
| **A-VEN** | Vendor / service provider | Publishes their offer and service area, receives connections, manages their profile. |
| **A-ADM** | Administrator / operator | Manages accounts, moderates content, oversees billing and statistics. |
| **A-SYS** | External systems | Authentication provider, payment service, email-sending service, geocoding service. |

---

## 4. Business model

Revenue is a **percentage success commission on the client's payment** for a booked activity. Because the commission is a share of the actual transaction, the payment **transits through the platform** (processed via Stripe Connect) rather than being self-reported by the vendor. This is settled in [ADR 0001](../decisions/0001-payment-stripe-connect.md) — superseding the earlier open choices DEC-01 (payment routing) and DEC-03 (monetization model) — and it conditions the functional requirements in §5.6 and the architecture.

---

## 5. Functional requirements

> Convention: `FR-xx` = functional requirement. Priority: **M** (must / essential for v1), **S** (should / desirable), **C** (could / later).

### 5.1 Accounts and profiles

| Code | Requirement | Prio |
|---|---|---|
| FR-01 | A visitor can create a client account or a vendor account. | M |
| FR-02 | Authentication by email + password, with email verification and password reset. | M |
| FR-03 | A user can view and edit their profile, and delete their account (right to erasure, see §6.6). | M |
| FR-04 | Each profile carries a **preferred language** (DE/EN), used for the interface, emails, and notifications. | M |
| FR-05 | Login via third-party provider (Google, etc.). | S |

### 5.2 Vendor profile and offer

| Code | Requirement | Prio |
|---|---|---|
| FR-10 | A vendor describes their offer: category(ies), description, presentation elements (text, images). | M |
| FR-11 | A vendor defines their **geographic service area** (see §5.5 for the modalities). | M |
| FR-12 | A vendor can indicate their availability (active / paused). | M |
| FR-13 | The descriptive profile content can be provided in the supported languages (see DEC-04 on data multilingualism). | S |
| FR-14 | A vendor views the history of connections concerning them. | M |

### 5.3 Expression of the client's need

| Code | Requirement | Prio |
|---|---|---|
| FR-20 | A client expresses their need through a simple guided flow (category, details, location). | M |
| FR-21 | The flow is **minimal in number of steps** and explicit (senior constraint, see §6.1). | M |
| FR-22 | The client provides their location (see §5.5). | M |
| FR-23 | A client can find the history of their requests and the associated connections. | S |

### 5.4 Matchmaking engine

The v1 engine is a **deterministic multi-criteria scoring**: for a client request, it associates a suitability score with each candidate vendor, then returns the highest ranked. It remains deliberately simple and explainable.

| Code | Requirement | Prio |
|---|---|---|
| FR-30 | For a client request, the engine establishes the list of candidate vendors and orders them by decreasing suitability score. | M |
| FR-31 | The score combines several weighted criteria, including at minimum: category / need suitability, **geographic proximity** (§5.5), vendor availability. | M |
| FR-32 | The criteria weights are **configurable** by the administrator, without redeployment. | S |
| FR-33 | The engine excludes vendors out of area / unavailable / not covering the requested category. | M |
| FR-34 | The result displayed to the client indicates the **distance** to the vendor and the elements justifying the relevance. | M |
| FR-35 | For each connection, the engine records the criteria and the score used (traceability, basis for future improvement). | S |
| FR-36 | Later evolution: adjusting the ranking based on preferences and observed usage (learning). | C |

### 5.5 Geolocation and distance

The distance between client and vendor is a central criterion of the engine. This domain deserves explicit treatment.

| Code | Requirement | Prio |
|---|---|---|
| FR-40 | The vendor defines their service area. **Modality to be arbitrated** (DEC-05): radius around an anchor point, or list of administrative zones (boroughs / postal codes), or a combination. | M |
| FR-41 | The client's location is obtained by address / postal code entry, and/or device geolocation (with consent). | M |
| FR-42 | The system computes the client ↔ vendor distance and uses it as a scoring criterion (FR-31) and as displayed information (FR-34). | M |
| FR-43 | The stored location precision must be **minimal and proportionate**: a reduced level of precision (postal code / locality) is preferred if the business need allows (see §6.6). | M |
| FR-44 | The user is informed of the use of their location and explicitly consents to it. | M |
| FR-45 | Handling of edge cases: missing or imprecise location (the engine must remain functional with a degraded distance criterion rather than failing). | S |

### 5.6 Monetization of the connection

*(The monetization model is settled — a percentage commission via Stripe Connect, [ADR 0001](../decisions/0001-payment-stripe-connect.md). These requirements reflect it; the payout window, cancellation, and dispute rules are also settled there.)*

| Code | Requirement | Prio |
|---|---|---|
| FR-50 | The system records each processed booking and the commission taken on it. | M |
| FR-51 | Collection via an external payment provider (Stripe Connect); **no sensitive payment data transits through or is stored by the platform**. | M |
| FR-52 | Payment confirmation comes exclusively from the provider (verified server-side mechanism), never from a browser-side action. | M |
| FR-53 | The vendor (and/or the administrator) views the billing / payout history. | M |

### 5.7 Search and discovery

| Code | Requirement | Prio |
|---|---|---|
| FR-60 | A client can browse / search vendors by category and area, outside the connection flow. | S |
| FR-61 | Simple filters (category, distance, availability). | S |

### 5.8 Notifications and communication

| Code | Requirement | Prio |
|---|---|---|
| FR-70 | The vendor is notified of a new connection concerning them (email at minimum; real-time in-interface notification desirable). | M |
| FR-71 | The client is notified of the result / acknowledgment of their request. | M |
| FR-72 | Notifications respect the recipient's preferred language (FR-04). | M |
| FR-73 | Modalities for later exchange between the parties after connection: **to be arbitrated** (DEC-02) — contact details exchanged vs. internal messaging. | S |

### 5.9 Back-office / administration

| Code | Requirement | Prio |
|---|---|---|
| FR-80 | The administrator manages accounts (validation, suspension, deletion). | M |
| FR-81 | The administrator moderates content (profiles, descriptions). | M |
| FR-82 | The administrator configures categories and engine weights (FR-32). | S |
| FR-83 | The administrator views usage and billing statistics. | M |

### 5.10 Usage tracking (analytics)

| Code | Requirement | Prio |
|---|---|---|
| FR-90 | The system records key usage events (requests, connections, views, unlocks). | M |
| FR-91 | This data feeds the administration statistics and, in time, the improvement of the engine (FR-36). | S |
| FR-92 | Collection respects the principles of minimization and consent (§6.6). | M |

---

## 6. Non-functional requirements

> Convention: `NFR-xx`.

### 6.1 Accessibility and adaptation to the senior audience

This is a **structuring** requirement, to be designed from the outset of the interface, not added afterwards.

| Code | Requirement |
|---|---|
| NFR-01 | Targeted compliance with the **WCAG 2.2 level AA** standard: sufficient contrasts, comfortable text sizes resizable without layout breakage, touch targets ≥ 44 px, visible focus, full keyboard navigation, screen-reader compatibility, semantic HTML and ARIA attributes. |
| NFR-02 | Senior adaptation beyond WCAG: short and linear flows, explicit labels rather than icons alone, clear and tolerant error messages, no hover-dependent interactions, strong consistency across screens. |
| NFR-03 | Accessibility tests and usability tests with representative users (including seniors) planned in the process. |

### 6.2 Multilingualism

| Code | Requirement |
|---|---|
| NFR-10 | The interface is available in German and English, with a language selector and respect for the profile's preferred language (FR-04). |
| NFR-11 | The internationalization architecture allows adding other languages without an overhaul. |
| NFR-12 | The multilingualism of **dynamic content** (vendor descriptions, categories) is handled according to arbitration DEC-04. |

### 6.3 Mobile-first and responsive

| Code | Requirement |
|---|---|
| NFR-20 | **Mobile-first** design: the experience is optimized for the phone first, then adapted to larger screens. |
| NFR-21 | Operation on recent mobile browsers (iOS Safari, Android Chrome) and on desktop. |

### 6.4 Performance

| Code | Requirement |
|---|---|
| NFR-30 | Matchmaking engine response time perceived as immediate (indicative target < 2 s per request, to be specified in the specs). |
| NFR-31 | Smooth interface on an average-quality mobile connection. |

### 6.5 Security

| Code | Requirement |
|---|---|
| NFR-40 | Any sensitive operation (billing, unlock, writing of critical data) is executed and validated **server-side**; the browser is never authoritative. |
| NFR-41 | Centralized authorization in a single source of truth (see §7), to avoid divergence of access rules. |
| NFR-42 | Encryption of exchanges (HTTPS), safe secret management, logging of sensitive accesses. |

### 6.6 Personal data protection

The processing of personal data, **and in particular location data**, imposes regulatory compliance to be specified depending on the target audiences.

| Code | Requirement |
|---|---|
| NFR-50 | Compliance with the **GDPR**. Scope is **Berlin only** ([ADR 0001](../decisions/0001-payment-stripe-connect.md)). |
| NFR-51 | **Minimization**: collect only the necessary data; for location, prefer the lowest granularity sufficient for the business (FR-43). |
| NFR-52 | Explicit consent for geolocation and usage collection; clear information about the purposes. |
| NFR-53 | Exercise of rights: access, rectification, erasure (consistent with FR-03), portability where applicable. |
| NFR-54 | Defined retention policy (lifetime of requests, locations, usage events). |

### 6.7 Maintainability and transferability

| Code | Requirement |
|---|---|
| NFR-60 | The main technology must remain **maintainable by a non-technical company** via a service provider: the choice is **Python** (broad talent pool, gentle learning curve). |
| NFR-61 | The code, the data schema, and the interface contract are documented so as to allow a third party to take over. |
| NFR-62 | Avoid any technological complexity not justified by the need (principle of architectural sobriety). |

---

## 7. Technical constraints

> *Appendix intended to frame the specifications; it does not require detailed business validation from the product owner. These choices will be detailed and may evolve during the specification phase.*

- **Backend: Python.** For maintainability and transferability (NFR-60). The business domain (profiles, matchmaking engine, monetization) and the application interface (API) are implemented in Python.
- **Database and core services: Supabase**, used as **managed PostgreSQL** surrounded by its authentication, file storage, and real-time notification services. The business logic does **not** reside in the database: the database carries data integrity (constraints, transactions), the Python backend carries the logic.
- **Single authority point for authorization**: access to data goes through the backend, which is the only place where business access rules apply (NFR-41). Database-level security mechanisms are, where applicable, defense in depth, not the source of truth.
- **Geodata**: the management of distances and zones relies on PostgreSQL's geospatial capabilities (geospatial extension available in Supabase), to be confirmed according to the chosen zone modality (DEC-05). An external geocoding service converts addresses into coordinates.
- **Interface (front)**: the existing prototype serves as a **UX reference**, not a code base. The target interface is rebuilt to satisfy accessibility, multilingualism, and mobile-first, and communicates with the backend via its API (never directly with the database).
- **Prototype → target strategy**: a quick prototype is acceptable for validating the flow and the engine, provided that the durable elements are preserved from the start — the **data schema** and the **API contract** — which must survive an implementation overhaul. The matchmaking engine may, if necessary and if maintenance skills allow, be isolated into a dedicated, more performant service later, without changing the schema.

---

## 8. Proposed iteration breakdown

*(Indicative, to be refined with the product owner after scope validation.)*

**Iteration 0 — Framing and durable foundation**
Validation of these specifications, arbitration of the §9 decisions, definition of the data schema and the API contract, choice of the geographic zone modality and the monetization model.

**Iteration 1 — Functional MVP**
Accounts and profiles (FR-01→04, FR-10→12), expression of the need (FR-20→22), basic geolocation (FR-40→44), matchmaking engine v1 (FR-30→34), email notification (FR-70→72), minimal back-office (FR-80, FR-83). Accessible, mobile-first, DE/EN interface on the main flow screens.

**Iteration 2 — Monetization**
Commission billing on processed payments (FR-50→53, [ADR 0001](../decisions/0001-payment-stripe-connect.md)), billing/payout history, supervision back-office.

**Iteration 3 — Enrichment**
Search / discovery (FR-60→61), configuration of weights (FR-32), multilingualism of dynamic content (FR-13), real-time notifications (FR-70), full usage tracking (FR-90→92).

**Later iterations**
Improvement of the engine through usage learning (FR-36), possible native application, additional languages.

---

## 9. Decisions to be arbitrated by the product owner

These points condition the specifications and must be settled before iteration 1. They are tracked, with their current status (several are now resolved by the decision records), in [open_questions/business/requirements.md](../open_questions/business/requirements.md).

---

*End of document — version 0.1 pending approval.*
