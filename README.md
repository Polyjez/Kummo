Kummo – Product Requirements Document (PRD)
Version: 2.0 (Glide-Aligned)
Date: May 21, 2026
Author: Poly Jeznita
Status: Ready for MVP Development

📌 1. Executive Summary
1.1 Mission Statement
By maximizing convenience, we remove the impediments so that quality time together can take center stage. With Kummo, we make family moments simple.
Kummo is a B2B2C platform that:
For Families/Seniors (B2C):
Simplifies the discovery and booking of family-friendly activities through hyper-personalization and community-driven recommendations.
For Businesses (B2B):
Automates backoffice tasks (reservations, payments, marketing) so they can focus on delivering their activities.
1.2 Business Model
Revenue Stream
Subscription fee from businesses (B2B). Free for users (B2C). Later, there will be a subscription for hyper-personalised recommendations.
Target Customers
B2B: Small/medium businesses offering activities (workshops, classes, events).
B2C: Families (parents with kids) and seniors in urban areas (e.g., Berlin).
Key Partners
Bookingkit and Regiondo (for payments and calendar sync).
Value Proposition
For Users: One-click booking, hyper-personalization, community.
For Businesses: Automated reservations, increased visibility, no technical hassle.

1.3 Alignment with Business Plan
B2B2C Model: Kummo connects businesses (B2B) with end-users (B2C) while handling all technical complexities.
Hyper-Personalization: Users receive tailored activity recommendations based on preferences (age, budget, location).
Community: Users can share reviews, recommendations, and interact (future feature).
Convenience: All barriers removed (no redirections, seamless booking, automated emails).

🎯 2. Product Overview
2.1 Core Value Proposition
For Users
For Businesses
✅ One-stop shop for family activities.
✅ Automated backoffice (no manual work).
✅ Hyper-personalized recommendations.
✅ Increased visibility (more customers).
✅ Seamless booking (no redirections).
✅ Integration with existing tools (Bookingkit/Regiondo).
✅ Community-driven (reviews, recommendations).
✅ Real-time data (reservations, payments).
✅ Mobile & web access.
✅ No technical setup required.

2.2 Key Features (MVP Scope)
🔹 User-Facing Features (B2C)
Feature
Description
Priority
Homepage
Landing page with search bar, hero section, and CTA ("Book Activities").
MVP
Activity Search
Filter activities by:
 - Age group (0-5, 6-12, 13-18, seniors).
 - Price range.
 - Location (map view).
 - Category (art, sports, cooking, etc.).
 - Date/Time.
MVP
Interactive Map
Visualize activities on a map (Google Maps).
MVP
Activity Details Page
Display:
 - Description.
 - Price.
 - Schedule.
 - Reviews/ratings.
 - Photos.
 - "Book Now" button.
MVP
Booking Flow
Users select activity → choose date/time → confirm booking → paiement. No redirection (via Bookingkit/Regiondo API + webhook).
MVP
User Profile
Personalized space to:
 - Save preferences (age, budget, location).
 - View booking history.
 - Favorite activities.
 - Leave reviews.
MVP
Email Notifications
Automated emails for:
 - Booking confirmation.
 - Reminders (24h before activity).
 - Feedback requests post-activity.
MVP
Chatbot
AI-powered chatbot to answer FAQs (e.g., "How do I book?" or "What activities are available for toddlers?").
MVP
Hyper-Personalization
Recommendations based on:
 - User preferences.
 - Past bookings.
 - Location.
 - Age group.
MVP

🔹 Business-Facing Features (B2B)
Feature
Description
Priority
Business Dashboard
Interface for businesses to:
 - Add/edit/delete activities.
 - View reservations.
 - Update availability.
MVP
Bookingkit/Regiondo Integration
API + Webhook connection to:
 - Sync calendars.
 - Process payments.
 - Avoid user redirection.
- Send cancellations.
MVP
CRM
Track:
 - Businesses (name, contact, activities offered).
 - Reservations (user, activity, date, status).
 - Revenue per business.
MVP
Automated Invoicing
Generate monthly invoices for businesses based on reservations.
MVP
Real-Time Calendar Sync
Businesses’ calendars (from Bookingkit/Regiondo) are always up-to-date on Kummo.
MVP
Customer Data Sharing
Send user data (name, email, booking details) to businesses after reservation.
MVP
Review Management
View and qualify user reviews (e.g., star ratings, comments).
MVP


🛠 3. Technical Requirements
3.1 System Architecture (Glide-Centric)
User (Web/Mobile)
   │
   ▼
Glide App (Front-End + Back-End) ──┬── Glide Data (Database)
   │                                │
   ▼                                ▼
Webhooks/Pipedream ─────────────── Bookingkit/Regiondo APIs
   │
   ▼
Gmail (Email Notifications)
   │
   ▼
Le Chat API (Chatbot)
3.2 Technology Stack
Component
Tool
Purpose
Cost
Notes

Front-End
Glide
Website + mobile app (PWA).
Free → $32/month
No-code, responsive, hosted.
Database
Glide Data Editor
Store activities, users, businesses, reservations, reviews.
Included
No need for Airtable.
API Integrations
Glide Webhooks + Pipedream
Connect to Bookingkit/Regiondo.
Free → $20/month
Pipedream for complex workflows.
Maps
Google Maps API
Interactive map for activities.
Free (limited)
Integrated in Glide.
Email
Gmail + Glide
Automated email notifications.
Free
Use with Glide automation.
Chatbot
Le Chat API + Botpress
AI-powered chatbot.
Free
Integrate via Glide or webhook.
Analytics
Google Analytics
Track user behavior.
Free
Add to Glide via custom code.

3.3 Data Flow (Glide + APIs)
User Books an Activity:
User selects activity in Glide → Glide creates a reservation record.
Glide Webhook sends data to Pipedream (or directly to Bookingkit/Regiondo API).
Bookingkit/Regiondo processes payment → sends confirmation to Pipedream.
Pipedream updates Glide Data (reservation status = "Confirmed") → triggers confirmation email via Gmail.
Business Updates Availability:
Business updates calendar in Bookingkit/Regiondo → triggers webhook.
Pipedream receives webhook → updates Glide Data (availability) in real-time.
User Receives Reminder:
Glide Data checks reservation date → Glide Automation triggers 24h before → sends reminder email via Gmail.

📅 4. MVP Scope & Timeline
4.1 MVP Definition
Minimum Viable Product (MVP) Goals:
User Side:
Search and filter activities.
View activity details, book and pay without leaving Kummo.
Receive confirmation/reminder emails.
Personalized recommendations.
Business Side:
Add/edit activities.
View reservations in real-time.
Receive user data after bookings.
Admin Side:
Track reservations and revenue per business.
Generate invoices.
Excluded from MVP (Future Features):
Advanced community features (chat, forums).
Multi-language support.
Native mobile apps (use PWA for now).
4.2 Timeline (4 Weeks)
Week
Tasks
Tools
Owner
Week 1
- Sign up for Glide.
 - Create Glide app (Marketplace template).
 - Set up Glide Data (Businesses, Activities, Users, Reservations, Reviews).
 - Contact 5-10 businesses to confirm Bookingkit/Regiondo usage.
Glide, Pipedream
Poly
Week 2
- Design Homepage, Activity Search, Activity Details, User Profile, Business Dashboard.
 - Add 10-20 fake activities for testing.
 - Set up Glide Chatbot (Le Chat API).
Glide, Le Chat API
Poly
Week 3
- Configure Webhooks (Glide → Pipedream → Bookingkit/Regiondo).
 - Set up email automation (confirmation, reminders).
 - Test with 5 fake users.
Glide, Pipedream, Gmail
Poly
Week 4
- Onboard 5 real businesses.
 - Collect feedback from businesses and users.
 - Fix bugs and refine MVP.
Glide, Pipedream
Poly


📊 5. Success Metrics (KPIs)
Metric
Target (MVP)
Measurement Tool
Number of Businesses Onboarded
10
Glide Data
Number of Activities Listed
50
Glide Data
Number of User Bookings
100
Glide Data
User Retention Rate
30% (returning users)
Google Analytics
Business Satisfaction Score
4.5/5 (survey)
Google Forms
Booking Conversion Rate
10% (visitors → bookings)
Google Analytics
Average Booking Value
€25
Glide Data


💰 6. Budget
Item
Cost (Monthly)
Notes
Glide
$0 (Free) → $32 (Pro)
Free tier sufficient for MVP.
Pipedream
$0 (Free) → $20 (Pro)
Free tier (100 workflows/month) sufficient for MVP.
Le Chat API
$0
Free for testing.
Google Maps API
$0 (Free tier)
Limited requests.
Total
$0
All tools have free tiers for MVP.


🚀 7. Why Glide Aligns with Kummo’s Needs
7.1 Business Plan Alignment
Business Plan Requirement
Glide Solution
How It Works
B2B2C Model
Glide supports user roles (businesses vs. families).
Separate dashboards for businesses and users.
Hyper-Personalization
Glide filters + user preferences.
Users see only relevant activities.
Community
Glide reviews + recommendations.
Users can leave reviews and rate activities.
Convenience (No Barriers)
Glide webhooks + API integrations.
Users book without leaving Kummo.
Backoffice Automation
Glide automation + Pipedream.
Businesses don’t need to manage reservations manually.
Real-Time Data
Glide webhooks + live updates.
Calendars and availability are always synced.

7.2 Technical Feasibility
Requirement
Glide Capability
Implementation
Website + Mobile App
✅ Yes (PWA + responsive).
Glide generates both.
Database
✅ Yes (Glide Data).
No need for Airtable.
API Integrations
✅ Yes (Webhooks + Pipedream).
Connect to Bookingkit/Regiondo.
User Profiles
✅ Yes.
Built-in user management.
Business Dashboards
✅ Yes.
Custom screens for businesses.
Email Automation
✅ Yes (Gmail).
Built-in or via Pipedream.
Chatbot
✅ Yes (Le Chat API).
Integrate via webhook.
Hyper-Personalization
✅ Yes (Filters + User Data).
Dynamic filtering.
CRM
✅ Yes (Glide Data).
Track businesses and reservations.
Invoicing
✅ Yes (Export CSV).
Generate invoices from Glide Data.


📝 8. Open Questions & Risks
8.1 Open Questions
Bookingkit/Regiondo API Access:
Do Bookingkit and Regiondo offer public APIs that Glide/Pipedream can connect to?
Action: Verify API documentation and test connectivity.
Business Adoption:
How will we convince businesses to use Kummo?
Action: Offer a free trial period and highlight time savings.
User Acquisition:
How will we attract families/seniors to Kummo?
Action: Partner with local influencers or community groups in Berlin.
8.2 Risks & Mitigation
Risk
Impact
Mitigation Plan
Bookingkit/Regiondo APIs are not accessible
Cannot integrate payments/calendars.
Use Pipedream or Zapier as a middleware.
Businesses refuse to adopt Kummo
Low supply of activities.
Offer free onboarding and demonstrate ROI.
Users don’t find value in Kummo
Low demand.
Focus on hyper-personalization and community features.
Glide limitations (SEO, scalability)
Long-term growth issues.
Migrate to custom solution (e.g., Next.js) after MVP validation.


🎯 9. Next Steps
9.1 Immediate Actions (Next 7 Days)
Sign up for **Glide** ([glideapps.com](https://www.glideapps.com/)).
Create a **Glide app** using the **Marketplace template**.
Set up **Glide Data** (tables: Businesses, Activities, Users, Reservations, Reviews).
Add **10-20 fake activities** for testing.
Contact **5-10 businesses** to confirm Bookingkit/Regiondo usage.
9.2 Dependencies
Dependency
Status
Next Action
Bookingkit API Access
⚠️ To verify
Check API docs and test connectivity.
Regiondo API Access
⚠️ To verify
Check API docs and test connectivity.
Business Onboarding
🟡 In progress
Contact local businesses in Berlin.

