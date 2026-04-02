# Народный Контроль — Product Requirements Document

## Original Problem Statement
Rebuild "Народный Контроль" (People's Control) into a modern full-stack web platform for civic engagement using FastAPI, React, MongoDB.

## Architecture
- **Frontend:** React.js + Tailwind CSS + Leaflet + Framer Motion + Shadcn/UI
- **Backend:** FastAPI + Motor (async MongoDB)
- **Auth:** Emergent-managed Google OAuth
- **Database:** MongoDB

## Implemented Features

### Phase 1 — Core
- Google Auth, user profiles, points/rating (7 tiers)
- Organizations CRUD + Leaflet map
- Review lifecycle: create → 2 verifications → approve/expire
- Admin panel (moderation, users, stats)
- Notifications, Rewards/shop, Referral program, File uploads, PWA, Leaderboard

### Phase 2 — Feature Expansion
- News Feed (`/news`): multi-level, categories, likes, comments
- Info Widgets (`/widgets`): weather, currency, magnetic storms, UV
- Problems Map (`/problems-map`): color-coded markers, filters
- Identity Verification (`/verification`): phone, passport, bank ID, Yandex ID

### Phase 3 — Legal Compliance & Support
- Support ticket system (`/support`): FAQ, 6 categories, replies, admin management
- Terms of Service (`/terms`), Privacy Policy (`/privacy`) — 152-FZ, 436-FZ compliant
- Consent checkboxes on login (terms + age 16+), Cookie banner
- Legal info API (`/api/legal/info`)

### Phase 4 — Quick Wins / User Engagement (Complete — Apr 2, 2026)
- **Interactive Onboarding** (3 steps + 20 bonus points)
- **Verification Feed** (`/verify`): pending reviews sorted by expiry, excludes own/already-verified
- **Social Sharing**: Telegram/VK/WhatsApp share buttons + copy link on reviews
- **Adaptive Verification Timer**: 72h (<50 users) → 48h → 24h → 12h (1000+)
- **Daily Missions + Streak**: 3 daily tasks (verify/read_news/visit_map), streak counter with x1.5 bonus at 7+ days
- **OG Meta Tags**: social sharing preview for links
- **Dashboard Redesign**: 3 quick action cards + daily missions widget

## Routes
| Route | Auth | Description |
|-------|------|-------------|
| `/login` | No | Login with consent |
| `/terms` | No | User agreement |
| `/privacy` | No | Privacy policy |
| `/dashboard` | Yes | Main + missions + onboarding |
| `/news` | Yes | News feed |
| `/verify` | Yes | Verification feed |
| `/widgets` | Yes | Weather/currency/magnetic |
| `/problems-map` | Yes | Problems map |
| `/map` | Yes | Organizations map |
| `/create` | Yes | Create review |
| `/rewards` | Yes | Rewards shop |
| `/verification` | Yes | Identity verification |
| `/support` | Yes | Support tickets |
| `/notifications` | Yes | Notifications |
| `/profile` | Yes | User profile |
| `/admin` | Yes (admin) | Admin panel |

## Prioritized Backlog

### P0 — People's Councils System
Hierarchical councils (Yard → District → City → Republic → Country) with discussions, voting, budgets

### P1 — Public Sector Reviews + Statistics Dashboard
Reviews for government services/officials + public analytics

### P2 — Future
- AI problem classification, Petitions, SOS button
- Business features (QR codes, verified accounts)
- Multi-language, accessibility, offline
- Telegram bot, District chats, Voice reviews
- Public org pages (SEO), Impact dashboard
- Refactoring server.py into modules
