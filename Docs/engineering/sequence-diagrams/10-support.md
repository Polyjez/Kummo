# 10. Contact support about a booking — UC 14

[← Index](README.md)

🔒 **Requires authentication** (Client) — request is tied to the client's booking.

> Open decision: *who* handles support (see brainstorming UC 14 "who?"). Modeled here as a support inbox.

```mermaid
sequenceDiagram
    actor Client
    participant Web
    participant API
    participant DB
    participant Mail

    Client->>Web: "I have a problem with my booking"
    Web->>API: POST /support {booking_id, message}
    API->>DB: store support request
    API->>Mail: forward to support inbox
    API->>Mail: acknowledgement to Client
    Mail-->>Client: "we received your request"
    API-->>Web: submitted
    Web-->>Client: confirmation
```

---

[← Reminder 24 h](09-reminder.md) · [Index](README.md) · [Next: Share a booking →](11-share-booking.md)
