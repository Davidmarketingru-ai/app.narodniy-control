# PRD - Народный Контроль (People's Control)

## Original Problem Statement
Rebuild uploaded React Native/Expo mobile app "Народный Контроль" as web application (FastAPI + React + MongoDB). All modules, Google Auth, Leaflet maps, modern design. Enhance with all recommended improvements.

## Architecture
- **Frontend**: React 19 + Tailwind CSS + Framer Motion + Leaflet/react-leaflet
- **Backend**: FastAPI (Python) + MongoDB (Motor async driver)
- **Auth**: Emergent Google OAuth (session-based with httpOnly cookies, SameSite=lax)
- **Database**: MongoDB
- **Maps**: Leaflet/OpenStreetMap with dark mode filter
- **PWA**: manifest.json + service worker
- **File Storage**: Server-side /uploads directory with API serving

## What's Been Implemented

### Phase 1 - MVP (Feb 19, 2026)
- Full FastAPI REST API with 20+ endpoints
- Emergent Google OAuth integration
- MongoDB with seeded data
- 8 pages: Login, Dashboard, Create Review, Map, Profile, Rewards, Notifications, Review Detail
- Leaflet map with color-coded category markers
- Dark "Civic Tactical" design

### Phase 2 - Enhancements (Feb 19, 2026)
1. Real Photo/Video Upload
2. PWA Manifest + Service Worker
3. Admin Moderation Panel (3 tabs)
4. Rating System (7 Statuses)
5. Automatic Review Expiry (24h timer)
6. Referral System

### Phase 3 - Auth Bug Fix (Feb 23, 2026)
**Problem**: After Google 2FA, user was redirected back to login page
**Root causes fixed**:
1. CORS: Infrastructure (K8s ingress) overrides `allow-origin:*`, conflicting with `credentials:true` — fixed by setting explicit CORS_ORIGINS in .env
2. Cookie: `SameSite=none` changed to `SameSite=lax` for same-origin compatibility
3. AuthCallback: Changed from React Router `navigate()` to `window.location.href` hard redirect for reliability — ensures page reloads with cookie
4. Added detailed backend logging for auth flow debugging
5. Improved error handling in AuthCallback with user-friendly error display

## Testing Status
- Phase 1: Backend 95%, Frontend 100%
- Phase 2: Backend 97.1%, Frontend 100%
- Phase 3: Auth flow 100% (infrastructure tested, real Google OAuth requires manual testing)

## Prioritized Backlog
### P1
- [ ] Leaderboard page (frontend)
- [ ] Organization management by owners
- [ ] Push notifications
- [ ] Review search and filtering

### P2
- [ ] Capacitor wrapping for native mobile apps
- [ ] Advanced analytics dashboard
- [ ] Gamification: achievements and badges
