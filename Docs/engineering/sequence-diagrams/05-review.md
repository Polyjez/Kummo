# 5. Review an activity after attending — UC 13

[← Index](README.md)

🔒 **Requires authentication** (Client) — and prior attendance is verified.

```mermaid
sequenceDiagram
    actor Client
    participant Web
    participant API
    participant DB

    Client->>Web: Open past booking, write review (rating + comment)
    Web->>API: POST /activities/{id}/reviews {rating, comment}
    API->>DB: verify client attended a past session of this activity
    alt eligible
        API->>DB: insert review
        API-->>Web: review saved
        Web-->>Client: thanks
    else not eligible
        API-->>Web: 403 must have attended
        Web-->>Client: explain
    end
```

---

[← Cancel & refund](04-cancel-refund.md) · [Index](README.md) · [Next: Client personal space →](06-client-space.md)
