# Kummo MVP – Technical Review

 **Purpose:** Identify the current technical and product bottlenecks, clarify what should be fixed first, and outline the next stages needed to turn the current prototype into a reliable MVP.

---

## 1. Executive Summary

The current Kummo project is a promising early prototype, but it is not yet a real marketplace MVP.

The main issue is not the visual design or the general idea. The core issue is that the project currently demonstrates parts of the intended user journey, but several critical marketplace functions are either missing, simulated, or stored only locally in the browser.

For the next phase, the priority should be to reduce the scope and make one core loop work reliably:

> A parent can find an activity, submit a real booking request, the business can see and manage that request, and the admin can monitor the process.

Everything else — payments, AI personalization, advanced calendar integrations, CRM, invoicing, and deep automation — should come after this core loop works with real data and real users.

---

## 2. Current State

The project currently works more like an interactive prototype than a production-ready MVP.

There are already useful parts:

- A basic public website structure
- Activity listing and detail pages
- Supabase connection
- Basic business/admin/profile pages
- Some early data models
- A working visual direction and product concept
- Initial thinking around users, businesses, and activities

However, several features that are described as part of the MVP are not yet implemented as real end-to-end product flows.

The current version should therefore be treated as:

> A clickable product prototype with some real database integration, not yet a validated transactional marketplace.

This is a good starting point, but the next step should be focused and disciplined.

---


## 3. Main Bottlenecks

### 3.1 The MVP Scope Is Too Broad

The current MVP description includes many ambitious features:

- Search and filtering
- Google Maps
- Activity detail pages
- Booking without redirect
- Payment integration
- Email notifications
- User profiles
- Favorites
- Reviews
- Chatbot
- Hyper-personalization
- B2B dashboard
- Bookingkit / Regiondo integrations
- CRM functions
- Invoices
- Calendar synchronization

This is too much for a first MVP.

The risk is that we spend too much time building many partial features, while the most important marketplace loop remains unreliable.

For the first real MVP, the scope should be reduced to:

1. Parents can discover activities.
2. Parents can submit a real booking request.
3. Businesses can see, confirm, or reject bookings.
4. Admins can monitor all activity and bookings.
5. Users and businesses receive basic email notifications.
6. The data is stored reliably and can be accessed from different devices.

This is enough to test the business idea.

---


### 3.2 Booking Is the Critical Missing Core

The most important missing piece is a real booking flow.

A marketplace is not validated by showing activities. It is validated when users try to book and businesses respond.

The current implementation appears to rely too much on browser-local state for some user actions. This means a booking may not behave like a real system-level event that is visible to the business and admin.

This should be fixed before adding more features.

The booking system should support at least:

- Activity reference
- Business / shop reference
- User / parent reference
- Date and time slot
- Number of children or participants
- Booking status:
 - requested
 - confirmed
 - rejected
 - cancelled
 - completed
- Contact information
- Timestamp
- Optional internal admin notes
- Future payment status field, even if payments are not implemented yet

The first version does not need fully automated payment or calendar synchronization. But it must store bookings in the database and make them visible to the right users.

---

### 3.3 Availability Is Not Yet Properly Solved

For Kummo, availability is a central product concept.

A parent does not only want to see that an activity exists. They need to know:

- When it happens
- Whether there are free places
- Whether it matches the child’s age
- Whether the location and time are realistic

The project needs a clear model for availability.

A simple first version could be:

- Activities have one or more availability slots.
- Each slot has:
 - start date/time
 - end date/time
 - capacity
 - booked count
 - status
- A booking is connected to one slot.

This does not need to be perfect at the beginning, but without a real availability model, the booking flow cannot become reliable.

---

### 3.4 Business Dashboard Needs to Become Operational

The business dashboard should not only be a place where providers can add or edit activities.

For the MVP, it should answer one question:

> Can a business actually manage the requests coming from parents?

The dashboard should support:

- Viewing incoming booking requests
- Seeing parent contact details
- Seeing activity, date, time, and number of participants
- Confirming or rejecting a request
- Editing or pausing activities
- Managing basic availability
- Seeing whether a booking is new, confirmed, rejected, or cancelled

This is much more important than advanced business analytics at the first stage.

---

### 3.5 Admin Dashboard Needs to Support Manual Operations

In the beginning, many marketplace operations will probably be manual. That is normal.

The admin dashboard should help the founding team operate the marketplace manually before everything is automated.

The admin should be able to:

- See all businesses
- See all activities
- See all bookings
- See booking statuses
- Search and filter bookings
- Manually update booking status if needed
- Identify failed or incomplete flows
- Help users and businesses when something goes wrong

This is not just an internal tool. It is part of making the MVP operational.

---

### 3.6 Some Features Look Implemented but Are Not Yet Real

Several features currently look like MVP functionality, but they are not yet complete end-to-end systems.

Examples:

- Booking may look like it works, but it does not yet behave like a reliable database-backed marketplace event.
- Map functionality is not yet a real location-based discovery flow.
- Chatbot functionality should not be treated as a core MVP feature.
- Personalization is too early unless there is enough real user and booking data.
- Payment and external booking integrations are too complex to prioritize before the basic booking flow works.

It is better to show fewer features that work reliably than many features that are only partially real.

---


## 4. What Should Be Fixed First

### Priority 0: Clarify the Real MVP

Before continuing implementation, we should define a smaller and more realistic MVP.

The MVP should not be described as a full marketplace automation platform yet.

The first MVP should be:

> A simple activity discovery and booking-request platform for parents and children’s activity providers in Berlin.

Recommended MVP documents:

- `MVP.md` – what exactly belongs to the first MVP
- `ROADMAP.md` – what comes later
- `ARCHITECTURE.md` – how data and user roles work
- `OPERATIONS.md` – how bookings are handled manually in the beginning

This will help avoid building in too many directions at once.

---

### Priority 1: Make Bookings Real

Bookings should be stored in the database and visible across:

- Parent profile
- Business dashboard
- Admin dashboard

A booking created by a parent should be visible to the business and admin immediately.

This is the most important technical step.

---

### Priority 2: Define Availability Slots

A real activity marketplace needs a real concept of time and capacity.

At minimum:

- One activity can have many slots.
- One slot can have many bookings.
- Each slot has capacity.
- Bookings should not exceed capacity.
- Businesses should be able to add or edit slots.

Even if this is simple at first, it needs to exist.

---

### Priority 3: Add User Roles and Permissions

The platform needs clear roles:

- Parent
- Business
- Admin

Each role should only access the data it is allowed to access.

This is especially important because the product may include information about children, bookings, and contact details.

At minimum:

- Parents see only their own bookings and children.
- Businesses see only their own activities and bookings.
- Admins can see everything.
- Public users can only see published activities and business information.

---

### Priority 4: Make the Business Dashboard Useful

The business dashboard should become the operational center for providers.

For the MVP, it should focus on:

- Booking requests
- Confirmation / rejection
- Activity management
- Availability management

Advanced analytics, CRM, and invoices can come later.

---

### Priority 5: Add Basic Notifications

Once bookings are real, the next step is notifications.

Minimum notifications:

- Parent receives confirmation that the request was submitted.
- Business receives notification about a new request.
- Parent receives confirmation or rejection after business action.

This can start simple. It does not need to be a complex notification system.

---

### Priority 6: Prepare for a Small Pilot

Before public launch, the platform should be tested with a very small number of real businesses and parents.

The goal should be to learn:

- Do parents understand the flow?
- Do they trust the platform enough to submit a booking?
- Do businesses understand and respond to requests?
- Which information is missing before booking?
- Which activities are actually attractive?
- Where does the process break?

This is more valuable than adding more features too early.

---


## 5. Suggested Product Stages

### Stage 1: Prototype Cleanup

Goal:

> Make the current prototype honest, stable, and easier to continue.

Tasks:

- Update product documentation
- Remove or mark unfinished features clearly
- Clean up configuration and environment setup
- Make data loading consistent
- Fix obvious broken flows
- Align the project with the actual technical direction

Outcome:

> A clean prototype that accurately represents what works and what does not.

---

### Stage 2: Real MVP Core

Goal:

> Make the core marketplace loop real.

Tasks:

- Database-backed bookings
- Availability slots
- Parent profile with real bookings
- Business dashboard with booking management
- Admin dashboard with operational overview
- Basic role permissions
- Basic notifications

Outcome:

> A parent can submit a real booking request and the business can manage it.

---

### Stage 3: Pilot With Real Users

Goal:

> Validate demand and operational workflow.

Tasks:

- Add a small number of real businesses
- Add real activity data
- Invite a small number of parents
- Track the booking funnel
- Manually support failed bookings
- Collect feedback from both sides

Outcome:

> We know whether the marketplace loop is valuable and where users struggle.

---

### Stage 4: Transaction Layer

Goal:

> Move from booking requests to actual transactions.

Tasks:

- Payment flow
- Cancellation rules
- Refund handling
- Payment status
- Booking status history
- Receipts or basic invoices
- Admin support tools

Outcome:

> Kummo becomes a real transactional marketplace.

---

### Stage 5: Provider Automation

Goal:

> Make it easier for businesses to manage their supply.

Tasks:

- Better activity management
- Recurring activity slots
- Calendar import or sync
- External booking platform integrations
- Provider onboarding
- Moderation tools
- Business analytics

Outcome:

> Businesses can manage their presence with less manual support.

---

### Stage 6: Personalization and Growth

Goal:

> Improve discovery and retention after real usage data exists.

Tasks:

- Better recommendations
- Favorites
- Reviews
- Child-age-based suggestions
- Location-based suggestions
- Personalized emails
- Repeat booking flows
- Growth experiments

Outcome:

> Kummo becomes more useful and personalized as users return.

---


## 6. Technical Direction

The current project can continue as a simple static prototype for the very short term, but this will become limiting once the MVP becomes more interactive.

A future migration to Svelte / SvelteKit should be considered.

This may be a better fit than moving directly to a heavier framework because:

- The product is still early.
- The UI can stay lightweight.
- The mental model is simple.
- It supports a gradual migration.
- It can work well with Supabase.
- It allows a better structure than plain HTML/JS without adding too much complexity.

A possible migration path:

1. Keep the current version working.
2. Extract the real data model and MVP flow first.
3. Start a SvelteKit version with:
 - public activity search
 - activity detail page
 - booking request flow
4. Move business/admin/profile pages gradually.
5. Keep Supabase as the backend until there is a strong reason to introduce a custom backend.

The key point: the next technical step should not be a full rewrite immediately. The priority is to define the real MVP and fix the core data flows. A framework migration should support that goal, not distract from it.

---

## 7. What Should Not Be Prioritized Yet

The following features should not be first priorities:

- Advanced AI chatbot
- Hyper-personalization
- Complex CRM
- Full invoice automation
- Deep Bookingkit / Regiondo integration
- Sophisticated analytics dashboard
- Advanced recommendation engine
- Full payment automation before booking requests work
- Complex design polish before the flow is reliable

These features may become important later, but they are not the current bottleneck.

---

## 8. Main Risks

### Risk 1: Building Too Much Before Validating the Core Loop

If we build too many features before the booking flow works, we may create complexity without learning whether the marketplace works.

### Risk 2: Confusing Prototype Behavior With Real Product Behavior

A feature that works only in one browser or only as a visual demo should not be treated as MVP-ready.

### Risk 3: Weak Data and Permission Model

Because the product may involve children, parents, bookings, and contact information, data access needs to be designed carefully from the beginning.

### Risk 4: External Integrations May Slow Down the MVP

Bookingkit, Regiondo, payments, calendar sync, and automation tools may be useful later, but they can delay the first usable version if introduced too early.

### Risk 5: Rewriting Too Early

A framework migration may be useful, but it should not happen before the real MVP scope is clear.

---

## 9. Recommended Next Steps

### Immediate Next Steps

1. Rewrite the MVP definition.
2. Define the real booking and availability model.
3. Move bookings into the database.
4. Build booking visibility across parent, business, and admin views.
5. Add basic role permissions.
6. Add basic notifications.
7. Prepare a small pilot with real activities.

### After That

1. Improve filters and discovery.
2. Add real map/location functionality.
3. Improve business self-service.
4. Add payments.
5. Add cancellation/refund logic.
6. Consider SvelteKit migration.
7. Add integrations only after the manual version proves demand.

---

## 10. Final Recommendation

The project has a good concept and a useful starting prototype, but the next step should be a strong focus on the core marketplace loop.

The question should not be:

> How do we implement all planned MVP features?

The better question is:

> What is the smallest reliable version that proves parents want to book activities through Kummo and businesses are willing to manage those bookings through the platform?

My recommendation is to build that version first.

Once the booking loop is real, we can decide what to automate, what to integrate, and which technical migration path makes the most sense.





