# Engineering documentation

Technical, developer-facing documentation — the *how*. Start here for the implementation view; the *what* (product intent) lives in [../product/](../product/), and the *why* behind key technical choices lives in [../decisions/](../decisions/).

## Reading order

0. **[implementation-status.md](implementation-status.md)** — what is built and what remains. The documents below describe the **target** and do not change as code lands; this one is the only current-state view. Read it first if you are picking up work.
1. **[specification.md](specification.md)** — the consolidated developer specification (entry point). Ties the product requirements, data model, flows, and decisions into one buildable reference. Contains `TODO` markers where sections are still to be authored.
2. **[data-model.md](data-model.md)** — conceptual ER model (entities, relationships, settled assumptions). Open modeling choices in [open_questions/technical/data-model.md](../open_questions/technical/data-model.md).
3. **[translations.md](translations.md)** — how the interface text (EN/DE) is maintained, written for whoever owns the wording rather than for developers. The mechanics are in [ADR 0005](../decisions/0005-localization-json-catalogues.md).
4. **[sequence-diagrams/](sequence-diagrams/)** — one flow per use case, following the target architecture (frontend → Python API → Supabase; server-side payment confirmation). See its [README](sequence-diagrams/README.md) for the use-case coverage map.

## Architecture in one paragraph

Python (FastAPI) backend owns all business logic and is the single authority for access rules and writes; the frontend never talks to the database directly. Supabase provides managed PostgreSQL + Auth/Storage/Realtime. Business-logic tables are accessed via SQLAlchemy 2.0 (async) ([ADR 0003](../decisions/0003-persistence-sqlalchemy.md)), with schema migrations written as Supabase CLI SQL ([ADR 0004](../decisions/0004-supabase-cli-single-migration-chain.md)); Storage/Auth use the Supabase client. Payments run through Stripe Connect with a custom booking module ([ADR 0001](../decisions/0001-payment-stripe-connect.md), [ADR 0002](../decisions/0002-booking-build-vs-buy.md)).

> Note: the archived [PRD (Glide MVP intent)](../archive/prd-glide-mvp.md) describes a *Glide* no-code MVP — historical product intent, superseded by the ADRs and not the target architecture documented here.
