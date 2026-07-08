# 3. Change a booking — UC 11

[← Index](README.md)

🔒 **Requires authentication** (Client) — acts on the client's own booking.

```mermaid
sequenceDiagram
    actor Client
    participant Web
    participant API
    participant DB
    participant Mail

    Client->>Web: Open booking, request change (new session/seats)
    Web->>API: PATCH /bookings/{id} {session_id?, seats?}
    API->>DB: check policy (deadline) + target session availability
    alt allowed
        API->>DB: release old seats, hold new seats, update booking
        API->>Mail: send updated confirmation to Client
        API->>DB: notification for Vendor (booking changed)
        API-->>Web: updated booking
        Web-->>Client: change confirmed
    else not allowed
        API-->>Web: 422 change not permitted
        Web-->>Client: explain (deadline passed / full)
    end
```

---

[← Book & pay](02-book-and-pay.md) · [Index](README.md) · [Next: Cancel & refund →](04-cancel-refund.md)
