# 2. Book & pay for an activity — UC 1, UC 2, UC 5, UC 21, UC 22, UC 23

[← Index](README.md)

🔒 **Requires authentication** (Client) — booking creates a record tied to the client's account.

The core flow. Multiple seats (UC 2), server-verified payment, seat decrement (UC 22), commission split (UC 21), confirmation email (UC 5), vendor notification (UC 23).

```mermaid
sequenceDiagram
    actor Client
    participant Web
    participant API
    participant Auth
    participant DB
    participant Pay
    participant Mail

    Client->>Web: Choose session + seats, "Book"
    Web->>API: POST /bookings {session_id, seats} (+ access token)
    API->>Auth: verify token
    Auth-->>API: user ok
    API->>DB: check session.seats_available >= seats
    alt not enough seats
        DB-->>API: insufficient
        API-->>Web: 409 seats unavailable
        Web-->>Client: choose another session
    else seats available
        API->>DB: create booking (status=pending), hold seats
        API->>Pay: create payment intent (amount)
        Pay-->>API: client_secret
        API-->>Web: booking pending + client_secret
        Web-->>Client: payment form
        Client->>Pay: submit payment details
        Pay-->>Web: payment result (UI only)

        Note over API,Pay: Authoritative confirmation is the webhook, not the browser
        Pay->>API: webhook payment_succeeded
        API->>DB: booking status=confirmed; seats_available -= seats
        API->>DB: record payment (amount, commission, vendor net)
        API->>Mail: send confirmation to Client (preferred language)
        Mail-->>Client: confirmation email
        API->>DB: create notification for Vendor
        API->>Mail: notify Vendor of new booking
        Mail-->>Vendor: booking notification
    end
```

---

[← Discover activities](01-discover-activities.md) · [Index](README.md) · [Next: Change a booking →](03-change-booking.md)
