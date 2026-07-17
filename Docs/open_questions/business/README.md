# Business — open questions

Product-owner / business-owner decisions still to arbitrate. Each entry links back to the document that owns the decision. See the [open-questions index](../README.md) for the full picture across business and technical.

| File | Covers | Blocking? |
|---|---|---|
| [payment.md](payment.md) | Payout timing, cancellation policy, dispute handling, commission structure, failed payouts, checkout transparency (owns [ADR 0001](../../decisions/0001-payment-stripe-connect.md)) | 3 blocking |
| [booking-build-vs-buy.md](booking-build-vs-buy.md) | In-house maintenance trade-off (owns [ADR 0002](../../decisions/0002-booking-build-vs-buy.md)) | validation |
| [requirements.md](requirements.md) | DEC-01…07 from the requirements §9 (several now resolved by ADR 0001) | mixed |

The three payment questions (OQ-PAY-1 payout timing, OQ-PAY-2 cancellation, OQ-PAY-3 disputes) gate the payment module and should be settled before iteration 1.
