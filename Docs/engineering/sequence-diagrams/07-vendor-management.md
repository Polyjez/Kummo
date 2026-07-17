# 7. Vendor manages shop & activities — UC 7, UC 8, UC 9, UC 18, UC 19

[← Index](README.md)

🔒 **Requires authentication** (Vendor). Login shown inline as the entry point to the vendor area.

Dashboard, add/edit activity (with categories & sessions), edit shop, preview.

```mermaid
sequenceDiagram
    actor Vendor
    participant Web
    participant API
    participant Auth
    participant DB

    Vendor->>Web: Log in
    Web->>Auth: signInWithPassword / OAuth
    Auth-->>Web: session

    Web->>API: GET /vendor/dashboard (token)
    API->>DB: shop(s), activities, sales, booking counts
    DB-->>API: data
    API-->>Web: dashboard (UC 7)
    Web-->>Vendor: activities & sales overview

    alt Add activity (UC 8)
        Vendor->>Web: New activity (title, price, ages, categories, sessions)
        Web->>API: POST /activities {...}
        API->>DB: insert activity, activity_category links, sessions
        API-->>Web: created
    else Edit activity (UC 9)
        Vendor->>Web: Edit activity
        Web->>API: PATCH /activities/{id} {...}
        API->>DB: update activity / categories / sessions
        API-->>Web: updated
    else Edit shop (UC 18)
        Vendor->>Web: Edit shop info
        Web->>API: PATCH /shops/{id} {...}
        API->>DB: update shop (re-geocode if address changed)
        API-->>Web: updated
    end

    Vendor->>Web: Preview public listing (UC 19)
    Web->>API: GET /activities/{id} (public view)
    API-->>Web: public detail
    Web-->>Vendor: how clients see it
```

---

[← Client personal space](06-client-space.md) · [Index](README.md) · [Next: Vendor cancel/reschedule →](08-vendor-cancel-reschedule.md)
