# Sequence diagrams — use case flows

Flow diagrams for the use cases in [brainstorming-en.md](../brainstorming-en.md). One file per flow; each heading notes the use cases (UC) it covers.

They follow the target architecture: the **frontend never talks to the database directly** — it goes through the **Python backend API**, which is the single authority for access rules and writes. Sensitive confirmations (payment) are validated **server-side**, never from the browser.

## Authentication marker

Each flow is tagged with its prerequisite:
- 🔓 **Public** — no sign-in required.
- 🔒 **Requires authentication** — the actor must already be signed in (see [Authentication](00-authentication.md)). Authenticated requests carry an access token that the API verifies with Supabase Auth on **every** call; that token check is shown once in [Authentication](00-authentication.md) and abbreviated as *"(auth token)"* elsewhere to keep the diagrams readable.
- ⚙️ **System flow** — no user session; runs as a trusted scheduled job.

## Participants

| Alias | Role |
|---|---|
| **Client** | Parent (end user, actor) |
| **Vendor** | Shop operator (actor) |
| **Web** | Web app / frontend (mobile-first) |
| **API** | Backend API (Python) — business logic, authority for access & writes |
| **Auth** | Supabase Auth (`auth.users` / `auth.identities`) |
| **DB** | Supabase Postgres (domain tables) |
| **Pay** | External payment provider (e.g. Stripe) |
| **Mail** | Email-sending service |
| **Geo** | Geocoding service (address → coordinates) |

## Table of contents

| # | Flow | Auth |
|---|---|---|
| 0 | [Authentication](00-authentication.md) — sign up, log in, request pattern, password reset | 🔒 |
| 1 | [Discover activities nearby & view details](01-discover-activities.md) | 🔓 |
| 2 | [Book & pay for an activity](02-book-and-pay.md) | 🔒 |
| 3 | [Change a booking](03-change-booking.md) | 🔒 |
| 4 | [Cancel a booking & get refunded](04-cancel-refund.md) | 🔒 |
| 5 | [Review an activity after attending](05-review.md) | 🔒 |
| 6 | [Client personal space](06-client-space.md) | 🔒 |
| 7 | [Vendor manages shop & activities](07-vendor-management.md) | 🔒 |
| 8 | [Vendor cancels or reschedules a session](08-vendor-cancel-reschedule.md) | 🔒 |
| 9 | [Reminder 24 h before an activity](09-reminder.md) | ⚙️ |
| 10 | [Contact support about a booking](10-support.md) | 🔒 |
| 11 | [Share a booking](11-share-booking.md) | 🔒 / 🔓 |

## Use-case coverage

Auth legend: 🔓 public · 🔒 requires sign-in · ⚙️ system/no user.

| UC | Description | Auth | Diagram |
|---|---|---|---|
| — | Sign up / log in / reset (prerequisite) | 🔒 | [0](00-authentication.md) |
| 1 | Find, book, pay in few steps | 🔓→🔒 | [1](01-discover-activities.md), [2](02-book-and-pay.md) |
| 2 | Book multiple seats | 🔒 | [2](02-book-and-pay.md) |
| 3 | Discover activities nearby | 🔓 | [1](01-discover-activities.md) |
| 4 | View activity info (no auth) | 🔓 | [1](01-discover-activities.md) |
| 5 | Confirmation email after payment | 🔒 | [2](02-book-and-pay.md) |
| 6 | Personalized client space | 🔒 | [6](06-client-space.md) |
| 7 | Vendor space (activities & sales) | 🔒 | [7](07-vendor-management.md) |
| 8 | Vendor add activity | 🔒 | [7](07-vendor-management.md) |
| 9 | Vendor edit activity | 🔒 | [7](07-vendor-management.md) |
| 10 | Reminder 24 h before | ⚙️ | [9](09-reminder.md) |
| 11 | Change booking | 🔒 | [3](03-change-booking.md) |
| 12 | Cancel booking + refund | 🔒 | [4](04-cancel-refund.md) |
| 13 | Review after attending | 🔒 | [5](05-review.md) |
| 14 | Contact support | 🔒 | [10](10-support.md) |
| 15 | Notified of change/cancellation | ⚙️ | [8](08-vendor-cancel-reschedule.md) |
| 16 | Vendor notifies cancellation | 🔒 | [8](08-vendor-cancel-reschedule.md) |
| 17 | Vendor notifies reschedule | 🔒 | [8](08-vendor-cancel-reschedule.md) |
| 18 | Vendor edit shop | 🔒 | [7](07-vendor-management.md) |
| 19 | Vendor previews listing | 🔒 | [7](07-vendor-management.md) |
| 20 | Share booking | 🔒 / 🔓 | [11](11-share-booking.md) |
| 21 | Vendor payment net of commission | 🔒 | [2](02-book-and-pay.md) |
| 22 | Seat count updates after booking | 🔒 | [2](02-book-and-pay.md) |
| 23 | Vendor notified of new booking | 🔒 | [2](02-book-and-pay.md) |
| 24 | Vendor notified of cancellation | 🔒 | [4](04-cancel-refund.md) |
