# 8. Vendor cancels or reschedules a session, clients notified — UC 15, UC 16, UC 17

[← Index](README.md)

🔒 **Requires authentication** (Vendor) — acts on the vendor's own sessions.

```mermaid
sequenceDiagram
    actor Vendor
    participant Web
    participant API
    participant DB
    participant Pay
    participant Mail

    alt Cancel session (UC 16)
        Vendor->>Web: Cancel a session
        Web->>API: POST /sessions/{id}/cancel
        API->>DB: session cancelled; list affected bookings
        loop each affected booking
            API->>Pay: refund(payment_ref)
            API->>DB: booking cancelled + refund recorded
            API->>Mail: notify Client of cancellation (UC 15)
            API->>DB: notification for Client
        end
        API-->>Web: done
    else Reschedule session (UC 17)
        Vendor->>Web: Change session date/time
        Web->>API: PATCH /sessions/{id} {starts_at, ends_at}
        API->>DB: update session; list affected bookings
        loop each affected booking
            API->>Mail: notify Client of new time (UC 15)
            API->>DB: notification for Client
        end
        API-->>Web: done
    end
    Web-->>Vendor: clients notified
```

---

[← Vendor management](07-vendor-management.md) · [Index](README.md) · [Next: Reminder 24 h →](09-reminder.md)
