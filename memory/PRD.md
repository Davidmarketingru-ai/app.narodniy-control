# Народный Контроль — PRD

## Architecture
React.js + FastAPI + MongoDB | Auth: Google OAuth | Jurisdiction: Kyrgyz Republic (PVT Bishkek)

## Implemented

### Core: Auth, Reviews (with mandatory photo+comment verification), Organizations, Map, Admin, Rewards, Referrals, PWA
### Phase 2: News Feed, Widgets (weather/currency/magnetic), Problems Map, Identity Verification
### Phase 3: Support Tickets + FAQ, Terms/Privacy (152-FZ, 436-FZ), Consent + Cookie Banner
### Phase 4: Onboarding, Verify Feed, Sharing, Adaptive Timer, Daily Missions + Streak
### Phase 5:
- **Mandatory verification proof**: photo + 20-char comment required
- **Gov Officials** (`/gov`): 15 allowed categories, blacklist (ФСБ/ФСО/СВР/ГРУ/military), reviews with ratings
- **Legal: Kyrgyzstan** (ОсОО, ПВТ, Бишкек) — no personal names anywhere
### Phase 6 (Current — Completed 2026-04-03):
- **People's Councils** (`/councils`): 5 levels (yard->district->city->republic->country)
  - Council creation with legal consent + 10 verifications required
  - Join/leave, discussions, votes, news
  - **AI-moderated news** via emergentintegrations (gpt-4o-mini): credibility scoring (high/medium/low/fake)
  - Representative nominations, elections, complaints
  - Frontend: 4 tabs (Discussions, Votes, News, Nominations), confirmation progress bars, AI labels

## Blacklisted Gov Keywords
фсб, фсо, свр, гру, разведк, контрразвед, спецслужб, спецназ, секретн, минобороны, генштаб, военн, росгвардия, нацгвардия

## Backlog
- P1: Public statistics dashboard, Public org pages (SEO), Telegram bot
- P2: District chats, Streak mechanics, Organization responses
- P3: Voice-to-text reviews, Offline mode (PWA), Refactoring server.py into modules
