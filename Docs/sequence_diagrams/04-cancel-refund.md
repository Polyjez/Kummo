# 4. Cancel a booking & get refunded — UC 12, UC 24

[← Index](README.md)

🔒 **Requires authentication** (Client) — acts on the client's own booking.

```mermaid
sequenceDiagram
    actor Client
    participant Web
    participant API
    participant DB
    participant Pay
    participant Mail

    Client->>Web: Cancel booking
    Web->>API: POST /bookings/{id}/cancel
    API->>DB: check cancellation policy
    alt refundable
        API->>Pay: refund(payment_ref, amount)
        Pay-->>API: refund ok
        API->>DB: booking status=cancelled; seats_available += seats; record refund
        API->>Mail: refund confirmation to Client
        API->>DB: notification for Vendor (booking cancelled)
        API->>Mail: notify Vendor of cancellation
        API-->>Web: cancelled + refunded
        Web-->>Client: confirmation
    else non-refundable window
        API->>DB: booking status=cancelled; seats_available += seats
        API-->>Web: cancelled, no refund
        Web-->>Client: explain policy
    end
```

---

[← Change a booking](03-change-booking.md) · [Index](README.md) · [Next: Review →](05-review.md)
