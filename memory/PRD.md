# Народный Контроль — PRD

## Architecture
React.js + FastAPI + MongoDB | Auth: Google OAuth | Jurisdiction: Kyrgyz Republic (PVT Bishkek)

## Council Hierarchy
- **Yard** — created manually (1 house = 1 council). Requires street + house_number.
- **District** — formed by escalation voting from yard councils.
- **City/Republic/Country** — each formed by voting from previous level.
- Formation threshold: 80% of verified residents at address.
- 10 confirmations required to activate any council.

## Implemented Features

### Core (Phase 1-5): Auth (Google OAuth), Reviews, Organizations, Map, Admin, Rewards, Referrals, News, Widgets, Problems Map, Verification, Support, Legal (KG), Onboarding, Daily Missions, Sharing, Gov Officials (blacklist), Mandatory verification

### Phase 6 — People's Councils:
- Hierarchical councils (yard->district->city->republic->country)
- Only yard-level manual creation, higher levels via escalation voting
- 80% formation tracking, AI-moderated news (emergentintegrations + gpt-4o-mini)
- Discussions, votes, nominations, elections, complaints
- Per-council mood gauge

### Phase 7 — P1 Features (Completed 2026-04-09):
- **Public Statistics** (`/stats`): Animated counters, mood gauge (6 levels: excellent/normal/mild_upset/dissatisfaction/stress/anger), councils by level, top organizations by rating. No auth required.
- **Public Org Pages** (`/org/{orgId}`): SEO-ready pages with reviews, rating distribution (1-5 stars), org info. No auth required.
- **Mood System**: Global + per-council mood tracking. Users set mood in profile and inside councils. Aggregated scores with dominant mood calculation.
- **Push Notifications**: Web Push API with VAPID keys, Service Worker (`sw-push.js`), subscribe/unsubscribe endpoints. Toggle in profile.
- **Telegram Bot Admin Panel**: Staff CRUD with 7 permission types (manage_reviews, manage_orgs, manage_councils, manage_users, view_stats, send_notifications, moderate_news). **MOCKED** — needs bot tokens from @BotFather.

## Blacklisted Gov Keywords
фсб, фсо, свр, гру, разведк, контрразвед, спецслужб, спецназ, секретн, минобороны, генштаб, военн, росгвардия, нацгвардия

## Backlog
- P1: Telegram bot actual implementation (needs tokens from user)
- P2: District chats (geo-fenced), Streak mechanics, Organization responses
- P3: Voice-to-text reviews, Offline mode (PWA), Refactoring server.py into modules
