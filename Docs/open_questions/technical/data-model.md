# Data model — open decisions

Open questions for the conceptual model in [data-model.md](../../engineering/data-model.md). Unresolved choices that require future work before the schema is finalized. Each changes the shape of one or more tables.

| # | Decision | Trade-off / impact | Status |
|---|---|---|---|
| OQ-DM-1 | **Seats & availability.** `seats_available` is modeled as a counter on `SESSION`. It could instead be derived by summing bookings. | Consistency-vs-simplicity trade-off (a counter can drift; a derived value costs a query per read). | Open |
| OQ-DM-2 | **Vendor ↔ Shop cardinality.** Assumed one vendor may own several shops. If it's strictly one shop per vendor, the two entities can merge. | Collapses two tables into one; affects ownership queries. | Open |
| OQ-DM-3 | **Notification polymorphism.** `recipient_id` + `recipient_type` point to either a client or a vendor. An alternative is separate notification tables per audience. | Polymorphic FK vs. two typed tables. | Open |
| OQ-DM-4 | **Not yet modeled.** Out of the MVP data core, will need their own modeling later: reviews of the *site* (vs. of an activity), community, chatbot, admin analytics (visitors, clicks, visit duration), booking sharing (UC 20). | Additive; does not block the MVP schema. | Deferred |

## Related

- Commission rate structure (single value vs. per-vendor/per-activity attribute) is an open question owned by the payment decision — see [../business/payment.md](../business/payment.md) (OQ-PAY-4). It affects whether `PAYMENT.commission` derives from a global rate or a stored per-entity rate.
