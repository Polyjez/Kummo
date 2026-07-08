# 9. Reminder 24 h before an activity — UC 10

[← Index](README.md)

⚙️ **System flow** — no user session; runs as a trusted scheduled job (no end-user authentication).

Time-triggered, no user in the loop.

```mermaid
sequenceDiagram
    participant Cron as Scheduler
    participant API
    participant DB
    participant Mail
    actor Client

    Cron->>API: trigger reminder job (hourly)
    API->>DB: sessions starting in ~24h with confirmed bookings
    DB-->>API: bookings to remind
    loop each booking
        API->>Mail: send reminder (Client preferred language)
        Mail-->>Client: reminder email
        API->>DB: mark reminder sent (idempotency)
    end
```

---

[← Vendor cancel/reschedule](08-vendor-cancel-reschedule.md) · [Index](README.md) · [Next: Contact support →](10-support.md)
