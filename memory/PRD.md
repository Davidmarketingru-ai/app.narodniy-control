# Народный Контроль — Product Requirements Document

## Original Problem Statement
Rebuild "Народный Контроль" (People's Control) into a modern full-stack web platform for civic engagement using FastAPI, React, MongoDB.

## Architecture
- **Frontend:** React.js + Tailwind CSS + Leaflet + Framer Motion + Shadcn/UI
- **Backend:** FastAPI + Motor (async MongoDB)
- **Auth:** Emergent-managed Google OAuth (dedicated /auth/callback route)
- **Database:** MongoDB

## Implemented Features

### Phase 1 — Core
- Google Auth, user profiles, points/rating (7 tiers)
- Organizations CRUD + Leaflet map
- Review lifecycle: create → 2 verifications → approve/expire
- Admin panel, Notifications, Rewards, Referral, File uploads, PWA, Leaderboard

### Phase 2 — Feature Expansion
- News Feed, Info Widgets (weather/currency/magnetic), Problems Map, Identity Verification

### Phase 3 — Legal Compliance & Support
- Support tickets + FAQ, Terms/Privacy (152-FZ, 436-FZ), Consent + Cookie banner

### Phase 4 — User Engagement
- Onboarding (3 steps), Verification Feed, Social Sharing, Adaptive Timer, Daily Missions + Streak

### Bug Fix — Mobile Auth (Apr 2, 2026)
- Dedicated `/auth/callback` route (unprotected) for Google OAuth redirect
- Multi-source session_id extraction (hash, query, regex, sessionStorage)
- Cookie SameSite changed to `none` for mobile browser compat
- Backward compat: any page with `#session_id` → redirect to callback
- Mobile error UI with retry button and help tip

## Routes
| Route | Auth | Description |
|-------|------|-------------|
| `/login` | No | Login with consent |
| `/auth/callback` | No | Google OAuth callback |
| `/terms` | No | User agreement |
| `/privacy` | No | Privacy policy |
| `/dashboard` | Yes | Main + missions |
| `/news` | Yes | News feed |
| `/verify` | Yes | Verification feed |
| `/widgets` | Yes | Weather/currency |
| `/problems-map` | Yes | Problems map |
| `/map` | Yes | Organizations |
| `/create` | Yes | Create review |
| `/rewards` | Yes | Rewards shop |
| `/verification` | Yes | Identity verification |
| `/support` | Yes | Support tickets |
| `/notifications` | Yes | Notifications |
| `/profile` | Yes | User profile |
| `/admin` | Yes (admin) | Admin panel |

## Backlog
- **P0:** People's Councils System
- **P1:** Public Sector Reviews + Statistics Dashboard
- **P2:** AI classification, Petitions, SOS, Telegram bot, District chats, Business features
