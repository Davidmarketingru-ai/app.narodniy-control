# Народный Контроль — PRD

## Architecture
React.js + FastAPI + MongoDB | Auth: Google OAuth | Jurisdiction: Kyrgyz Republic (PVT Bishkek)

## Council Hierarchy
- **Yard** — only manually created level (1 house = 1 council, requires street + house_number)
- **District/City/Republic/Country** — formed by escalation voting from previous level
- Formation threshold: 80% verified residents. 10 confirmations to activate.

## Implemented Features

### Phase 1-5: Auth, Reviews, Orgs, Map, Admin, Rewards, Referrals, News, Widgets, Problems Map, Verification, Support, Legal (KG), Onboarding, Missions, Sharing, Gov Officials (blacklist)

### Phase 6 — People's Councils:
- Hierarchical councils with escalation voting
- AI-moderated news (emergentintegrations + gpt-4o-mini)
- Discussions, votes, nominations, elections, complaints
- Per-council mood gauge

### Phase 7 — P1 Features:
- Public Statistics (`/stats`): Animated counters, mood gauge (6 levels), councils by level, top orgs
- Public Org Pages (`/org/{orgId}`): SEO pages with reviews, rating distribution
- Mood System: Global + per-council mood tracking
- Push Notifications: Web Push API + VAPID + Service Worker

### Phase 8 — P2 Features (Completed 2026-04-09):
- **Telegram Bot** (token: configured, @info_narkon_bot):
  - Account linking via deep link
  - Notification preferences (5 categories)
  - Admin commands with role-based access
  - Mass notifications, stats
  - Staff management with 7 permission types
- **District Chats** (`/district-chat`): Geo-fenced messaging by district, polling refresh
- **Streak System**: Daily check-in, milestones (3/7/14/30/60/100 days), point rewards
- **Organization Responses**: org_manager role, reply to reviews, admin can assign managers

## Blacklisted Gov Keywords
фсб, фсо, свр, гру, разведк, контрразвед, спецслужб, спецназ, секретн, минобороны, генштаб, военн, росгвардия, нацгвардия

## Backlog
- P3: Offline режим (Service Worker caching), рефакторинг server.py на модули (~2500 строк)
