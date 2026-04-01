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
- **News Feed** (`/news`): Multi-level (yard→world) news with categories, likes, comments, urgency flag
- **Info Widgets** (`/widgets`): Weather (open-meteo), Currency rates (CBR), Magnetic storms (NOAA), UV index
- **Problems Map** (`/problems-map`): Leaflet map with color-coded markers by status
- **Identity Verification** (`/verification`): Phone, Passport, Bank ID, Yandex ID — 3 levels

### Phase 3 — Legal Compliance & Support (Complete — Mar 10, 2026)
- **Support Ticket System** (`/support`): FAQ (8 items), ticket creation with 6 categories (bug, complaint, suggestion, question, rights_violation, other), replies, status management (open/in_progress/resolved/closed), priority system, admin ticket management
- **Terms of Service** (`/terms`): Full 9-section user agreement with placeholder legal entity data, references to ГК РФ, УК РФ ст.128.1, КоАП ст.5.61, ФЗ-282, ФЗ-38
- **Privacy Policy** (`/privacy`): Full 9-section policy compliant with 152-ФЗ, references to Роскомнадзор, DPO contact, data storage on RF territory
- **Consent System**: Mandatory checkboxes on login (terms acceptance + age 16+ per ФЗ-436), consent recorded in user profile with timestamp and IP
- **Cookie Banner**: Persistent cookie consent notification with localStorage tracking
- **Legal Info API**: `/api/legal/info` returns operator details (placeholder ИНН, ОГРН, address)

## Key Pages & Routes
| Route | Auth | Description |
|-------|------|-------------|
| `/login` | No | Login with consent checkboxes |
| `/terms` | No | User agreement |
| `/privacy` | No | Privacy policy |
| `/dashboard` | Yes | Main dashboard |
| `/news` | Yes | News feed |
| `/widgets` | Yes | Weather, currency, magnetic |
| `/problems-map` | Yes | Problems map |
| `/map` | Yes | Organizations map |
| `/create` | Yes | Create review |
| `/rewards` | Yes | Rewards shop |
| `/verification` | Yes | Identity verification |
| `/support` | Yes | Support tickets + FAQ |
| `/notifications` | Yes | Notifications |
| `/profile` | Yes | User profile |
| `/admin` | Yes (admin) | Admin panel |

## Prioritized Backlog

### P0 — System of People's Councils
Hierarchical council system (Yard → District → City → Republic → Country) with:
- Discussion forums, Voting mechanisms, Budget management, Member approval workflows

### P1 — Reviews for Public Sector
- Extend reviews to government services (hospitals, schools, police)
- Rate individual officials

### P1 — Statistics Dashboard
- Public analytics: city/district ratings, solved vs unsolved problems

### P2 — Future Features
- AI-powered problem classification and routing
- Petitions system with escalation
- SOS emergency button
- Business features (QR codes, verified accounts)
- Multi-language support, accessibility, offline mode
- Refactoring server.py into modular APIRouter structure
