# PRD — Kummo (Glide MVP intent, v2.0)

|  |  |
|---|---|
| **Version** | 2.0 (Glide-aligned) |
| **Date** | 21 May 2026 |
| **Author** | Poly Jeznita |
| **Original status** | "Ready for MVP development" |

!!! warning "Superseded — historical product intent"
    This PRD captures the original **Glide no-code MVP** vision. It is kept for historical context only and does **not** describe the current build. Its three load-bearing choices have since been superseded:

    - **Revenue = B2B subscription** → superseded by [ADR 0001](../decisions/0001-payment-stripe-connect.md): a **percentage commission** on the client's payment, processed via **Stripe Connect**.
    - **Bookingkit / Regiondo for booking & payments** → superseded by [ADR 0002](../decisions/0002-booking-build-vs-buy.md): a **dedicated booking module** built in-house (Regiondo was explicitly evaluated and rejected).
    - **Glide / Pipedream / Le Chat stack** → superseded by [ADR 0003](../decisions/0003-persistence-sqlalchemy.md) and the [engineering docs](../engineering/README.md): the build is a hand-coded **FastAPI + Supabase + SQLAlchemy** application.

    For the current product need see [product/requirements.md](../product/requirements.md); for the current architecture see [engineering/](../engineering/README.md).

---

## 1. Executive summary

### 1.1 Mission statement

> By maximizing convenience, we remove the impediments so that quality time together can take center stage. With Kummo, we make family moments simple.

Kummo is a B2B2C platform that:

- **For families / seniors (B2C):** simplifies discovering and booking family-friendly activities through hyper-personalization and community-driven recommendations.
- **For businesses (B2B):** automates back-office tasks (reservations, payments, marketing) so they can focus on delivering their activities.

### 1.2 Business model

| Aspect | Description |
|---|---|
| **Revenue stream** | Subscription fee from businesses (B2B). Free for users (B2C). Later, a subscription for hyper-personalized recommendations. |
| **Target customers** | **B2B:** small/medium businesses offering activities (workshops, classes, events). **B2C:** families (parents with kids) and seniors in urban areas (e.g. Berlin). |
| **Key partners** | Bookingkit and Regiondo (payments and calendar sync). |
| **Value proposition** | *For users:* one-click booking, hyper-personalization, community. *For businesses:* automated reservations, increased visibility, no technical hassle. |

### 1.3 Alignment with the business plan

- **B2B2C model:** Kummo connects businesses (B2B) with end-users (B2C) while handling all technical complexities.
- **Hyper-personalization:** users receive tailored activity recommendations based on preferences (age, budget, location).
- **Community:** users can share reviews, recommendations, and interact (future feature).
- **Convenience:** all barriers removed (no redirections, seamless booking, automated emails).

---

## 2. Product overview

### 2.1 Core value proposition

| For users | For businesses |
|---|---|
| One-stop shop for family activities | Automated back-office (no manual work) |
| Hyper-personalized recommendations | Increased visibility (more customers) |
| Seamless booking (no redirections) | Integration with existing tools (Bookingkit / Regiondo) |
| Community-driven (reviews, recommendations) | Real-time data (reservations, payments) |
| Mobile & web access | No technical setup required |

### 2.2 Key features (MVP scope)

**User-facing (B2C)** — all MVP priority:

| Feature | Description |
|---|---|
| Homepage | Landing page with search bar, hero section, and CTA ("Book Activities"). |
| Activity search | Filter by age group (0–5, 6–12, 13–18, seniors), price range, location (map view), category (art, sports, cooking, …), date/time. |
| Interactive map | Visualize activities on a map (Google Maps). |
| Activity details page | Description, price, schedule, reviews/ratings, photos, "Book Now" button. |
| Booking flow | Select activity → choose date/time → confirm → pay. No redirection (via Bookingkit/Regiondo API + webhook). |
| User profile | Save preferences (age, budget, location), view booking history, favorite activities, leave reviews. |
| Email notifications | Booking confirmation, reminders (24 h before), post-activity feedback requests. |
| Chatbot | AI-powered chatbot for FAQs ("How do I book?", "What activities suit toddlers?"). |
| Hyper-personalization | Recommendations based on preferences, past bookings, location, age group. |

**Business-facing (B2B)** — all MVP priority:

| Feature | Description |
|---|---|
| Business dashboard | Add/edit/delete activities, view reservations, update availability. |
| Bookingkit/Regiondo integration | API + webhook to sync calendars, process payments, avoid redirection, send cancellations. |
| CRM | Track businesses (name, contact, activities), reservations (user, activity, date, status), revenue per business. |
| Automated invoicing | Generate monthly invoices for businesses based on reservations. |
| Real-time calendar sync | Business calendars (Bookingkit/Regiondo) always up-to-date on Kummo. |
| Customer data sharing | Send user data (name, email, booking details) to businesses after reservation. |
| Review management | View and qualify user reviews (star ratings, comments). |

---

## 3. Technical requirements

### 3.1 System architecture (Glide-centric)

```
User (Web/Mobile)
   │
   ▼
Glide App (Front-End + Back-End) ──┬── Glide Data (Database)
   │                               │
   ▼                               ▼
Webhooks / Pipedream ───────────── Bookingkit / Regiondo APIs
   │
   ▼
Gmail (Email Notifications)
   │
   ▼
Le Chat API (Chatbot)
```

### 3.2 Technology stack

| Component | Tool | Purpose | Cost | Notes |
|---|---|---|---|---|
| Front-end | Glide | Website + mobile app (PWA). | Free → $32/mo | No-code, responsive, hosted. |
| Database | Glide Data Editor | Store activities, users, businesses, reservations, reviews. | Included | No need for Airtable. |
| API integrations | Glide Webhooks + Pipedream | Connect to Bookingkit/Regiondo. | Free → $20/mo | Pipedream for complex workflows. |
| Maps | Google Maps API | Interactive activity map. | Free (limited) | Integrated in Glide. |
| Email | Gmail + Glide | Automated email notifications. | Free | Use with Glide automation. |
| Chatbot | Le Chat API + Botpress | AI-powered chatbot. | Free | Integrate via Glide or webhook. |
| Analytics | Google Analytics | Track user behavior. | Free | Add to Glide via custom code. |

### 3.3 Data flow (Glide + APIs)

- **User books an activity:** user selects activity in Glide → Glide creates a reservation record → Glide webhook sends data to Pipedream (or directly to Bookingkit/Regiondo) → provider processes payment → confirmation returns to Pipedream → Pipedream sets reservation status = "Confirmed" and triggers a confirmation email via Gmail.
- **Business updates availability:** business updates its calendar in Bookingkit/Regiondo → webhook fires → Pipedream updates Glide Data (availability) in real time.
- **User receives a reminder:** Glide Automation checks the reservation date and, 24 h before, sends a reminder email via Gmail.

---

## 4. MVP scope & timeline

### 4.1 MVP definition

- **User side:** search and filter activities; view details, book and pay without leaving Kummo; receive confirmation/reminder emails; personalized recommendations.
- **Business side:** add/edit activities; view reservations in real time; receive user data after bookings.
- **Admin side:** track reservations and revenue per business; generate invoices.
- **Excluded from MVP (future):** advanced community features (chat, forums); multi-language support; native mobile apps (PWA for now).

### 4.2 Timeline (4 weeks)

| Week | Tasks | Tools |
|---|---|---|
| Week 1 | Sign up for Glide; create Glide app (Marketplace template); set up Glide Data (Businesses, Activities, Users, Reservations, Reviews); contact 5–10 businesses to confirm Bookingkit/Regiondo usage. | Glide, Pipedream |
| Week 2 | Design Homepage, Activity Search, Activity Details, User Profile, Business Dashboard; add 10–20 fake activities; set up chatbot (Le Chat API). | Glide, Le Chat API |
| Week 3 | Configure webhooks (Glide → Pipedream → Bookingkit/Regiondo); set up email automation (confirmation, reminders); test with 5 fake users. | Glide, Pipedream, Gmail |
| Week 4 | Onboard 5 real businesses; collect feedback; fix bugs and refine MVP. | Glide, Pipedream |

*(Owner for all weeks: Poly.)*

---

## 5. Success metrics (KPIs)

| Metric | Target (MVP) | Measurement tool |
|---|---|---|
| Businesses onboarded | 10 | Glide Data |
| Activities listed | 50 | Glide Data |
| User bookings | 100 | Glide Data |
| User retention rate | 30% (returning users) | Google Analytics |
| Business satisfaction score | 4.5/5 (survey) | Google Forms |
| Booking conversion rate | 10% (visitors → bookings) | Google Analytics |
| Average booking value | €25 | Glide Data |

---

## 6. Budget

| Item | Cost (monthly) | Notes |
|---|---|---|
| Glide | $0 (Free) → $32 (Pro) | Free tier sufficient for MVP. |
| Pipedream | $0 (Free) → $20 (Pro) | Free tier (100 workflows/mo) sufficient for MVP. |
| Le Chat API | $0 | Free for testing. |
| Google Maps API | $0 (free tier) | Limited requests. |
| **Total** | **$0** | All tools have free tiers for MVP. |

---

## 7. Why Glide aligns with Kummo's needs

### 7.1 Business-plan alignment

| Requirement | Glide solution | How it works |
|---|---|---|
| B2B2C model | User roles (businesses vs. families) | Separate dashboards for businesses and users. |
| Hyper-personalization | Filters + user preferences | Users see only relevant activities. |
| Community | Reviews + recommendations | Users can leave reviews and rate activities. |
| Convenience (no barriers) | Webhooks + API integrations | Users book without leaving Kummo. |
| Back-office automation | Glide automation + Pipedream | Businesses don't manage reservations manually. |
| Real-time data | Webhooks + live updates | Calendars and availability always synced. |

### 7.2 Technical feasibility

| Requirement | Glide capability | Implementation |
|---|---|---|
| Website + mobile app | Yes (PWA + responsive) | Glide generates both. |
| Database | Yes (Glide Data) | No need for Airtable. |
| API integrations | Yes (Webhooks + Pipedream) | Connect to Bookingkit/Regiondo. |
| User profiles | Yes | Built-in user management. |
| Business dashboards | Yes | Custom screens for businesses. |
| Email automation | Yes (Gmail) | Built-in or via Pipedream. |
| Chatbot | Yes (Le Chat API) | Integrate via webhook. |
| Hyper-personalization | Yes (filters + user data) | Dynamic filtering. |
| CRM | Yes (Glide Data) | Track businesses and reservations. |
| Invoicing | Yes (export CSV) | Generate invoices from Glide Data. |

---

## 8. Open questions & risks

### 8.1 Open questions

- **Bookingkit/Regiondo API access** — do they offer public APIs that Glide/Pipedream can connect to? *Action:* verify API docs and test connectivity.
- **Business adoption** — how to convince businesses to use Kummo? *Action:* offer a free trial and highlight time savings.
- **User acquisition** — how to attract families/seniors? *Action:* partner with local influencers or community groups in Berlin.

### 8.2 Risks & mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| Bookingkit/Regiondo APIs not accessible | Cannot integrate payments/calendars. | Use Pipedream or Zapier as middleware. |
| Businesses refuse to adopt Kummo | Low supply of activities. | Free onboarding, demonstrate ROI. |
| Users don't find value | Low demand. | Focus on hyper-personalization and community. |
| Glide limitations (SEO, scalability) | Long-term growth issues. | Migrate to a custom solution after MVP validation. |

---

## 9. Next steps

### 9.1 Immediate actions (next 7 days)

1. Sign up for [Glide](https://www.glideapps.com/).
2. Create a Glide app using the Marketplace template.
3. Set up Glide Data (tables: Businesses, Activities, Users, Reservations, Reviews).
4. Add 10–20 fake activities for testing.
5. Contact 5–10 businesses to confirm Bookingkit/Regiondo usage.

### 9.2 Dependencies

| Dependency | Status | Next action |
|---|---|---|
| Bookingkit API access | To verify | Check API docs and test connectivity. |
| Regiondo API access | To verify | Check API docs and test connectivity. |
| Business onboarding | In progress | Contact local businesses in Berlin. |
