# Technical — open questions

Engineering decisions still to arbitrate. Each entry links back to the document that owns the decision. See the [open-questions index](../README.md) for the full picture across business and technical.

| File | Covers | Blocking? |
|---|---|---|
| [data-model.md](data-model.md) | Seats/availability model, vendor↔shop cardinality, notification polymorphism, not-yet-modeled areas (owns [data model](../../engineering/data-model.md)) | non-blocking |
| [persistence.md](persistence.md) | Team SQLAlchemy/Alembic conventions (owns [ADR 0003](../../decisions/0003-persistence-sqlalchemy.md)) | onboarding |
