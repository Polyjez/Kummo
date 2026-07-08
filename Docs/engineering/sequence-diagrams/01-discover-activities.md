# 1. Discover activities nearby & view details — UC 3, UC 4

[← Index](README.md)

🔓 **Public** — no authentication required.

```mermaid
sequenceDiagram
    actor Client
    participant Web
    participant API
    participant DB
    participant Geo

    Client->>Web: Open activities page (address or "near me")
    opt address entered
        Web->>API: GET /activities?location=<address>&filters
        API->>Geo: geocode(address)
        Geo-->>API: lat/lng
    end
    Web->>API: GET /activities?lat&lng&age&category&price&slot&keyword
    API->>DB: query activities join shop (location), categories
    DB-->>API: matching activities + shop location
    API->>API: compute distance (client ↔ shop) & sort
    API-->>Web: activities (with distance)
    Web-->>Client: map + tiles (top 4, then results)

    Client->>Web: Click an activity
    Web->>API: GET /activities/{id}
    API->>DB: fetch activity, shop, sessions, avg rating
    DB-->>API: activity detail
    API-->>Web: full detail
    Web-->>Client: activity page (no auth needed)
```

---

[← Authentication](00-authentication.md) · [Index](README.md) · [Next: Book & pay →](02-book-and-pay.md)
