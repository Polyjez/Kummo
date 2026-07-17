# 0. Authentication

[← Index](README.md)

Prerequisite for every 🔒 flow. Login is delegated to **Supabase Auth**; the same account model serves Client and Vendor (separate accounts). These flows are referenced by all authenticated use cases rather than repeated in them.

## A. Sign up — create a Client or Vendor account

```mermaid
sequenceDiagram
    actor User as Client / Vendor
    participant Web
    participant Auth
    participant API
    participant DB
    participant Mail

    User->>Web: Fill sign-up form (email, password, role)
    Web->>Auth: signUp(email, password)
    Auth->>Auth: create auth.users + email identity
    Auth->>Mail: send verification email
    Mail-->>User: verify your email
    Auth-->>Web: session (unverified)
    User->>Mail: click verification link
    Mail->>Auth: confirm email
    Web->>API: POST /clients | /vendors (profile data + auth token)
    API->>Auth: verify token
    Auth-->>API: user id
    API->>DB: create Client/Vendor profile (user_id -> auth.users.id)
    API-->>Web: profile created
    Web-->>User: account ready
```

## B. Log in — email/password or Google (delegated)

```mermaid
sequenceDiagram
    actor User as Client / Vendor
    participant Web
    participant Auth
    participant Google as Google (IdP)

    alt Email + password
        User->>Web: Enter email & password
        Web->>Auth: signInWithPassword(email, password)
        Auth-->>Web: session (access + refresh token)
    else Google OAuth (account linking)
        User->>Web: "Continue with Google"
        Web->>Auth: signInWithOAuth(google)
        Auth->>Google: OAuth authorization
        Google-->>User: consent screen
        User->>Google: approve
        Google-->>Auth: id token (provider_id)
        Auth->>Auth: match/link auth.identities to auth.users
        Auth-->>Web: session (access + refresh token)
    end
    Web-->>User: signed in
    Note over Web,Auth: Access token is attached to every 🔒 API request
```

## C. Authenticated request pattern (reused by every 🔒 flow)

```mermaid
sequenceDiagram
    participant Web
    participant API
    participant Auth
    participant DB

    Web->>API: request + Authorization: Bearer <access token>
    API->>Auth: verify token
    alt valid
        Auth-->>API: user id (+ role)
        API->>DB: perform authorized action
        DB-->>API: result
        API-->>Web: 200 result
    else invalid / expired
        Auth-->>API: rejected
        API-->>Web: 401 Unauthorized
        Note over Web: refresh token or redirect to login
    end
```

## D. Password reset — email/password accounts

```mermaid
sequenceDiagram
    actor User
    participant Web
    participant Auth
    participant Mail

    User->>Web: "Forgot password"
    Web->>Auth: resetPasswordForEmail(email)
    Auth->>Mail: send reset link
    Mail-->>User: reset link
    User->>Web: open link, set new password
    Web->>Auth: updateUser(password)
    Auth-->>Web: password updated
    Web-->>User: sign in with new password
```

---

[← Index](README.md) · [Next: Discover activities →](01-discover-activities.md)
