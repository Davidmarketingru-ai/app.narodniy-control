# Народный Контроль — PRD

## Architecture
React.js + FastAPI + MongoDB | Auth: Google OAuth | Jurisdiction: Kyrgyz Republic (PVT Bishkek)

## Council Hierarchy (Core Feature)
- **Yard (Дворовый)** — only level created manually. One house = one council. Requires street + house_number.
- **District (Районный)** — formed by escalation voting from yard councils in the same district.
- **City (Городской)** — formed by escalation voting from district councils.
- **Republic (Республиканский)** — formed from city councils.
- **Country (Народный)** — formed from republic councils.

### Formation Rules
- Yard council requires 10 confirmations from verified users to activate.
- A yard council is "formed" when 80% of verified residents at that address are members.
- Escalation: chairman/rep of a formed council can initiate vote to create next-level council.
- All same-level councils in the area vote; majority creates the next level automatically.
- One address can only have one yard council (duplicate check).

## Implemented Features

### Phase 1-4: Auth (Google OAuth), Reviews, Organizations, Map, Admin, Rewards, Referrals, News, Widgets, Problems Map, Verification, Support, Legal (KG), Onboarding, Daily Missions, Sharing
### Phase 5: Mandatory verification (photo+comment), Gov Officials (blacklisted: ФСБ/ФСО/СВР/ГРУ), Legal Kyrgyzstan anchoring
### Phase 6 (Completed 2026-04-04):
- **People's Councils** with hierarchical escalation system
- Yard-only manual creation with address binding
- 80% formation threshold tracking
- Escalation voting for higher-level councils
- AI-moderated news (emergentintegrations + gpt-4o-mini)
- Discussions, votes, nominations, elections, complaints
- User address fields in profile
- Frontend: FormationBar, EscalationTab, 5 tabs in detail view

## Blacklisted Gov Keywords
фсб, фсо, свр, гру, разведк, контрразвед, спецслужб, спецназ, секретн, минобороны, генштаб, военн, росгвардия, нацгвардия

## Backlog
- P1: Public statistics dashboard, Public org pages (SEO), Telegram bot
- P2: District chats, Streak mechanics, Organization responses
- P3: Voice-to-text reviews, Offline mode (PWA), Refactoring server.py into modules
