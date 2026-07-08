# 6. Client personal space — UC 6

[← Index](README.md)

🔒 **Requires authentication** (Client). The login shown here is the [Authentication](00-authentication.md) flow, included inline because this is the entry point to the authenticated area.

History, favorites, children, preferences.

```mermaid
sequenceDiagram
    actor Client
    participant Web
    participant API
    participant Auth
    participant DB

    Client->>Web: Log in
    Web->>Auth: signInWithPassword / OAuth (Google)
    Auth-->>Web: session (access token)
    Web->>API: GET /me/dashboard (token)
    API->>Auth: verify token
    API->>DB: fetch client profile, children, bookings, favorites
    DB-->>API: data
    API-->>Web: personalized space
    Web-->>Client: history, favorites, children, prefs
```

---

[← Review](05-review.md) · [Index](README.md) · [Next: Vendor management →](07-vendor-management.md)
