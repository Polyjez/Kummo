# Open questions

Everything still to arbitrate, gathered in one place and split by audience. Each entry links back to the document that owns the decision (an ADR, the requirements, or the data model). When a question is settled, record the outcome in its owning document and mark the row **Resolved** here.

```
open_questions/
├── business/    Product-owner / business-owner decisions
└── technical/   Engineering decisions
```

## Business — [business/](business/)

| File | Covers | Blocking? |
|---|---|---|
| [payment.md](business/payment.md) | Payout timing, cancellation policy, dispute handling, commission structure, failed payouts, checkout transparency (owns [ADR 0001](../decisions/0001-payment-stripe-connect.md)) | 3 blocking |
| [booking-build-vs-buy.md](business/booking-build-vs-buy.md) | In-house maintenance trade-off (owns [ADR 0002](../decisions/0002-booking-build-vs-buy.md)) | validation |
| [requirements.md](business/requirements.md) | DEC-01…07 from the requirements §9 (several now resolved by ADR 0001) | mixed |

## Technical — [technical/](technical/)

| File | Covers | Blocking? |
|---|---|---|
| [data-model.md](technical/data-model.md) | Seats/availability model, vendor↔shop cardinality, notification polymorphism, not-yet-modeled areas (owns [data model](../engineering/data-model.md)) | non-blocking |
| [persistence.md](technical/persistence.md) | Team SQLAlchemy/Alembic conventions (owns [ADR 0003](../decisions/0003-persistence-sqlalchemy.md)) | onboarding |

## Blocking the build first

The three payment questions in [business/payment.md](business/payment.md) (OQ-PAY-1 payout timing, OQ-PAY-2 cancellation, OQ-PAY-3 disputes) gate the payment module and should be settled before iteration 1.
