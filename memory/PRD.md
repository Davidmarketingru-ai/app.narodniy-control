# Народный Контроль — PRD

## Architecture
React.js + FastAPI + MongoDB | Auth: Google OAuth | Jurisdiction: Kyrgyz Republic (PVT Bishkek)

## Implemented

### Core: Auth, Reviews (with mandatory photo+comment verification), Organizations, Map, Admin, Rewards, Referrals, PWA
### Phase 2: News Feed, Widgets (weather/currency/magnetic), Problems Map, Identity Verification
### Phase 3: Support Tickets + FAQ, Terms/Privacy (152-FZ, 436-FZ), Consent + Cookie Banner
### Phase 4: Onboarding, Verify Feed, Sharing, Adaptive Timer, Daily Missions + Streak
### Phase 5 (Current):
- **Mandatory verification proof**: photo + 20-char comment required
- **Gov Officials** (`/gov`): 15 allowed categories, blacklist (ФСБ/ФСО/СВР/ГРУ/military), reviews with ratings
- **Legal: Kyrgyzstan** (ОсОО, ПВТ, Бишкек) — no personal names anywhere
- **People's Councils** (`/councils`): 5 levels (yard→country), discussions, voting, membership, chairman role

## Blacklisted Gov Keywords
фсб, фсо, свр, гру, разведк, контрразвед, спецслужб, спецназ, секретн, минобороны, генштаб, военн, росгвардия, нацгвардия

## Backlog
- P1: Public statistics dashboard, Public org pages (SEO)
- P2: AI classification, Petitions, SOS, Telegram bot, District chats, Voice reviews
- P2: Business features, Multi-language, Offline mode
- P3: Refactoring server.py into modules
