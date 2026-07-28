# Open questions

Everything still to arbitrate, gathered in one place and split by audience. Each entry links back to the document that owns the decision (an ADR, the requirements, or the data model). When a question is settled, record the outcome in its owning document and delete its row here — git history retains the original question and answer.

```
open_questions/
├── business/    Product-owner / business-owner decisions
└── technical/   Engineering decisions
```

## Business — [business/](business/)

Payment (ADR 0001) had no remaining open questions and its tracking file was removed — see [ADR 0001](../decisions/0001-payment-stripe-connect.md).

| File | Covers | Blocking? |
|---|---|---|
| [booking-build-vs-buy.md](business/booking-build-vs-buy.md) | In-house maintenance trade-off (owns [ADR 0002](../decisions/0002-booking-build-vs-buy.md)) | validation |
| [requirements.md](business/requirements.md) | DEC-02, DEC-04, DEC-05, DEC-07 from the requirements §9 (DEC-01/03/06 resolved by ADR 0001, removed) | mixed |

## Technical — [technical/](technical/)

| File | Covers | Blocking? |
|---|---|---|
| [data-model.md](technical/data-model.md) | Seats/availability model, vendor↔shop cardinality, notification polymorphism, not-yet-modeled areas (owns [data model](../engineering/data-model.md)) | non-blocking |
| [persistence.md](technical/persistence.md) | Team SQLAlchemy/Alembic conventions (owns [ADR 0003](../decisions/0003-persistence-sqlalchemy.md)) | onboarding |
