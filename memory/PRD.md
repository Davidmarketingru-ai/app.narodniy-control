# PRD - Народный Контроль (People's Control)

## Original Problem Statement
Rebuild uploaded React Native/Expo mobile app "Народный Контроль" as a web application using Python (FastAPI) + React + MongoDB. All modules, Google Auth, Leaflet maps, new modern design. Then enhance with all recommended improvements.

## Architecture
- **Frontend**: React 19 + Tailwind CSS + Framer Motion + Leaflet/react-leaflet
- **Backend**: FastAPI (Python) + MongoDB (Motor async driver)
- **Auth**: Emergent Google OAuth (session-based with httpOnly cookies)
- **Database**: MongoDB (collections: users, user_sessions, organizations, reviews, verifications, notifications, rewards, points_history)
- **Maps**: Leaflet/OpenStreetMap with dark mode filter
- **PWA**: manifest.json + service worker for offline caching
- **File Storage**: Server-side /uploads directory with API serving

## User Personas
1. **Citizen Reporter** (18-60+): Creates reviews about expired products, dirty stores, overpriced goods
2. **Verifier**: Confirms/validates reviews from other users
3. **Rewards Seeker**: Earns points for creating/verifying reviews, exchanges for rewards
4. **Admin/Moderator**: Manages reviews, users, and platform statistics

## Core Requirements (Static)
- Google OAuth authentication
- Dashboard with reviews feed, stats, quick actions
- Create Review with org selection, text, rating, real photo/video upload
- Interactive Leaflet map centered on Vladikavkaz
- Review verification system (2 confirmations required)
- Points & Rewards system (age-group adapted)
- Notifications center
- User profile with settings (theme, text scale, age group)
- Dark/Light theme toggle
- Responsive design (desktop sidebar + mobile bottom nav)
- Russian language UI throughout

## What's Been Implemented

### Phase 1 - MVP (Feb 19, 2026)
- Full FastAPI REST API with 20+ endpoints
- Emergent Google OAuth integration
- MongoDB with seeded data (8 orgs, 5 reviews, 11 rewards)
- 8 pages: Login, Dashboard, Create Review, Map, Profile, Rewards, Notifications, Review Detail
- Leaflet map with color-coded category markers
- Dark "Civic Tactical" design with Manrope + JetBrains Mono fonts

### Phase 2 - Enhancements (Feb 19, 2026)
1. **Real Photo/Video Upload** - POST /api/upload endpoint with multipart/form-data, server-side storage, file serving via /api/uploads/{filename}
2. **PWA Manifest** - manifest.json + service worker (sw.js) for installability and offline caching
3. **Admin Moderation Panel** - Full admin page with 3 tabs (Reviews/Users/Stats), approve/reject reviews with reasons, user role management
4. **Rating System (7 Statuses)** - Новичок → Наблюдатель → Контролёр → Инспектор → Эксперт → Мастер → Легенда, with progress bars and color coding
5. **Automatic Review Expiry** - Background async task checks every 5 minutes for pending reviews past 24h, auto-marks as "expired" with notification
6. **Referral System** - Unique 8-char referral codes, 50 pts for referrer + 25 pts for referred, copy-to-clipboard, apply form, stats tracking

## Testing Status
- Phase 1: Backend 95%, Frontend 100%
- Phase 2: Backend 97.1%, Frontend 100%
- All features functional end-to-end

## Prioritized Backlog
### P1 (Important)
- [ ] Leaderboard page (frontend) showing top users
- [ ] Organization management by owners
- [ ] Push notifications (browser)
- [ ] Review search and filtering

### P2 (Nice to Have)
- [ ] Capacitor wrapping for AppStore/Google Play native apps
- [ ] User-to-user messaging for review coordination
- [ ] Advanced analytics dashboard for admins
- [ ] Review categories and tags
- [ ] Gamification: achievements and badges

## Next Tasks
1. Leaderboard frontend page
2. Capacitor integration for native mobile apps
3. Organization owner self-service portal
