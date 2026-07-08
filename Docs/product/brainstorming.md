# Brainstorming

**Goal:** B2B2C platform / marketplace connecting parents with workshops (ateliers).

!!! note "Historical brainstorm"
    Early, pre-decision notes kept for context. Where an item here conflicts with the [decision records](../decisions/README.md) — e.g. booking tooling ([ADR 0002](../decisions/0002-booking-build-vs-buy.md)) or the commission / payout model ([ADR 0001](../decisions/0001-payment-stripe-connect.md)) — the ADRs govern. The use-case numbers (UC 1–24) are referenced by the [sequence diagrams](../engineering/sequence-diagrams/README.md), so they are kept stable.

## MVP

### Home page

- [ ] Hero section: photo, text, CTA button
- [ ] Activity search engine: filters, activity categorization
- [ ] Activity showcase: top 4
- [ ] "How Kummo works" section: clients, vendors
- [ ] Site reviews
- [ ] Footer

### Activities page

- [ ] Map: activities placed on the map
- [ ] Filters: age, category, location, time slot, price, keyword
- [ ] Tiles: top 4, then filter results

### "Client" profile page

- [ ] Log in
- [ ] Sign-up form: last name, first name, email, age, interests, address, preferred time slots, number of children
- [ ] Children sign-up form: first name, date of birth, interests, gender
- [ ] Favorites
- [ ] History

### "Vendor" page

- [ ] Log in
- [ ] Sign-up form: shop name, address, phone, email, activity type
- [ ] Activity registration form
- [ ] Number of activities offered
- [ ] Total number of bookings

### "Admin" page — Dashboard

- [ ] Number of vendors, clients, activities, booked activities
- [ ] Number of visitors, clicks per page, visit duration

## Features

- **Booking** — dedicated in-house module (see [ADR 0002](../decisions/0002-booking-build-vs-buy.md))
- **Payment solution** — [Stripe](https://stripe.com) (Stripe Connect, see [ADR 0001](../decisions/0001-payment-stripe-connect.md))
- **AI recommendations / personalization**
- **Community**
- **Chatbot**

## Use cases

1. As a client, I want to find, book, and pay for an activity in as few steps and clicks as possible (activity page, or home page with authentication).
2. As a client, I want to book multiple seats in the same workshop (authenticated activity page).
3. As a client, I want to see all the activities around where I live (activities page).
4. As a client, I want all the important information about an activity before choosing (activity page, no authentication).
5. As a client, I want a confirmation email after payment (client's personal inbox).
6. As a client, I want my own personalized space (authenticated client page).
7. As a vendor, I want my own space to view my activities and my sales through the platform (authenticated vendor page).
8. As a vendor, I want to add activities myself (authenticated vendor page).
9. As a vendor, I want to edit my activities' data myself (authenticated vendor page).
10. As a client, I want a reminder email 24 h before the activity (client's personal inbox).
11. As a client, I want to change my booking if I have a conflict or made a mistake (email).
12. As a client, I want to cancel my booking and be refunded if I have a conflict or made a mistake (email).
13. As a client, I want to review an activity after taking part in it (authenticated client page).
14. As a client, I want to contact someone if I have a problem with my booking (email — who?).
15. As a client, I want to be notified if there is a change or cancellation to an activity I signed up for (email).
16. As a vendor, I want to notify my Kummo clients when I have to cancel an activity (email).
17. As a vendor, I want to notify my Kummo clients when I have to reschedule an activity (email).
18. As a vendor, I want to edit my shop information myself (authenticated vendor page).
19. As a vendor, I want to see how my activities are presented (home page or activity page — public page accessible?).
20. As a client, I want to share my booking with other users (authenticated client page — share? users = clients?).
21. As a vendor, I want to receive my payment already net of commission directly upon booking.
22. As a vendor, I want my booking system to update the number of available seats after a booking made through Kummo.
23. As a vendor, I want a notification when a booking is placed through Kummo.
24. As a vendor, I want a notification when a booking is cancelled through Kummo.

## Vocabulary

- **Client**
- **Vendor**
- **Shop** — the entity that organizes the activities
- **Activity**
- **Seat** (in an activity)
- **Booking**
- **Payment**
- **Review**
- **Personal space** / **Client space**
- **Vendor space**
- **Home page**
- **Client page**
- **Activity page**

## Actions

### Client

- Geographically locate activities near their place of residence
- View the details of an activity
- Book one or more seats within an activity
- Pay for a booking
- Cancel a booking
- Modify a booking
- View their personalized space
- Receive a refund
- Review a workshop
- Share their booking

### Vendor

- Add an activity
- Modify an activity
- Communicate a cancellation to their clients
- Edit shop information
- Get paid
- Update the number of remaining seats

## Notifications

### Client

- Booking payment confirmation
- Reminder the day before a workshop
- Workshop cancellation
- Workshop change

### Vendor

- Booking confirmation
- Client cancellation

## TODO

- [ ] Define each vocabulary term
- [ ] Clarify the highlighted items
- [ ] Propose a possible breakdown into batches (prioritize features to define iterations)
