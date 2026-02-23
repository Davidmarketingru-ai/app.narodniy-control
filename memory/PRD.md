# Народный Контроль — Product Requirements Document

## Original Problem Statement
Rebuild a React Native application "Народный Контроль" (People's Control) into a modern full-stack web application using Python (FastAPI), React, and MongoDB. The platform enables civic engagement through verified community reviews, news feeds, problem mapping, and eventually a hierarchical People's Councils system.

## Core Architecture
- **Frontend:** React.js + Tailwind CSS + Shadcn/UI + Leaflet + Framer Motion
- **Backend:** FastAPI + Motor (async MongoDB) + Pydantic
- **Database:** MongoDB
- **Auth:** Emergent-managed Google OAuth (custom callback flow)
- **Fonts:** Manrope + JetBrains Mono

## What's Been Implemented

### Phase 1 — Core (Complete)
- Google Auth with session management
- User profiles with points/rating system (7 tiers: Новичок → Легенда)
- Organizations CRUD with map display (Leaflet)
- Review lifecycle: create → verify (2 confirmations) → approve/expire
- Admin panel: review moderation, user management, stats
- Notifications system
- Rewards/shop with age-group targeting
- Referral program (+50/+25 points)
- File uploads (images/video)
- PWA support
- Rating leaderboard

### Phase 2 — Feature Expansion (Complete — Feb 23, 2026)
- **News Feed** (`/news`): Multi-level (yard→world) news with categories, likes, comments, urgency flag, create form
- **Info Widgets** (`/widgets`): Weather (open-meteo), Currency rates (CBR), Magnetic storms (NOAA), UV index, Location search
- **Problems Map** (`/problems-map`): Leaflet map with color-coded markers by status, filters, linked to reviews
- **Identity Verification** (`/verification`): Phone (SMS code), Passport (hashed), Bank ID (Sber/Tinkoff/VTB/Alfa), Yandex ID — 3 verification levels (basic → confirmed → verified)

## API Endpoints
### Auth
- POST `/api/auth/session` — Google auth callback
- GET `/api/auth/me` — Current user
- POST `/api/auth/logout`

### Content
- GET/POST `/api/reviews`, GET `/api/reviews/{id}`
- POST `/api/verifications`, GET `/api/verifications/{review_id}`
- GET/POST `/api/organizations`, GET `/api/organizations/{id}`
- GET/POST `/api/news`, GET `/api/news/{id}`, POST `/api/news/{id}/like`
- GET/POST `/api/news/{id}/comments`

### Widgets
- GET `/api/widgets/weather?lat=&lon=`
- GET `/api/widgets/currency`
- GET `/api/widgets/magnetic`
- GET `/api/widgets/locations?q=`

### Map
- GET `/api/map/problems`

### User
- GET/PUT `/api/profile`
- GET `/api/rating/status`, GET `/api/rating/leaderboard`
- POST `/api/referral/apply`, GET `/api/referral/stats`
- GET `/api/verification/status`, POST `/api/verification/phone`, etc.

### Admin
- GET `/api/admin/reviews`, PUT `/api/admin/reviews/{id}/approve|reject`
- GET `/api/admin/stats`, GET `/api/admin/users`

## Prioritized Backlog

### P0 — System of People's Councils
Hierarchical council system (Yard → District → City → Republic → Country) with:
- Discussion forums
- Voting mechanisms
- Budget management
- Member approval workflows

### P1 — Reviews for Public Sector
- Extend reviews to government services (hospitals, schools, police)
- Rate individual officials

### P1 — Statistics Dashboard
- Public analytics: city/district ratings, solved vs unsolved problems
- Individual contribution tracking

### P2 — Future Features
- AI-powered problem classification and routing
- Petitions system with escalation
- SOS emergency button
- Business features (QR codes, verified accounts)
- Multi-language support, accessibility, offline mode

## Technical Notes
- Auth flow uses non-standard Google OAuth callback (workaround for CORS)
- `server.py` is a monolith — refactoring into APIRouter modules recommended
- Widget APIs use free tiers (open-meteo, CBR, NOAA) — designed for easy replacement
- Seed data exists for organizations, reviews, news
