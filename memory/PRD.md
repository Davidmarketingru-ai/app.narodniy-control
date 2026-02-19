# PRD - Народный Контроль (People's Control)

## Original Problem Statement
Rebuild uploaded React Native/Expo mobile app "Народный Контроль" as a web application using Python (FastAPI) + React + MongoDB. All modules, Google Auth, Leaflet maps, new modern design.

## Architecture
- **Frontend**: React 19 + Tailwind CSS + Framer Motion + Leaflet/react-leaflet
- **Backend**: FastAPI (Python) + MongoDB (Motor async driver)
- **Auth**: Emergent Google OAuth (session-based with httpOnly cookies)
- **Database**: MongoDB (collections: users, user_sessions, organizations, reviews, verifications, notifications, rewards, points_history)
- **Maps**: Leaflet/OpenStreetMap with dark mode filter

## User Personas
1. **Citizen Reporter** (18-60+): Creates reviews about expired products, dirty stores, overpriced goods
2. **Verifier**: Confirms/validates reviews from other users by visiting the location
3. **Rewards Seeker**: Earns points for creating/verifying reviews, exchanges for rewards

## Core Requirements
- [x] Google OAuth authentication (Emergent)
- [x] Dashboard with reviews feed, stats, quick actions
- [x] Create Review with org selection, text, rating, photos
- [x] Interactive Leaflet map centered on Vladikavkaz with color-coded markers
- [x] Review verification system (2 confirmations required)
- [x] Points & Rewards system (age-group adapted)
- [x] Notifications center
- [x] User profile with settings (theme, text scale, age group)
- [x] Dark/Light theme toggle
- [x] Responsive design (desktop sidebar + mobile bottom nav)
- [x] Russian language UI throughout

## What's Been Implemented (Feb 19, 2026)
### Backend
- Full FastAPI REST API with 20+ endpoints
- Emergent Google OAuth integration
- MongoDB collections with seeded data (8 orgs, 5 reviews, 11 rewards)
- Review creation, verification, points awarding system
- Notifications system (auto-generated on events)
- Rewards redemption

### Frontend  
- Modern dark "Civic Tactical" design with Manrope + JetBrains Mono fonts
- Glassmorphism card design with colored borders
- 8 pages: Login, Dashboard, Create Review, Map, Profile, Rewards, Notifications, Review Detail
- Leaflet map with color-coded category markers
- Framer Motion animations throughout
- Responsive layout (sidebar desktop, bottom nav mobile)

## Testing Status
- Backend: 95% pass (all endpoints working, minor 201 status fix applied)
- Frontend: 100% pass (all pages rendering, responsive, design verified)

## Prioritized Backlog
### P0 (Critical)
- None remaining

### P1 (Important)
- [ ] Real file upload for review photos/videos (currently placeholder)
- [ ] Review expiry automation (24h timer)
- [ ] Admin moderation panel

### P2 (Nice to Have)
- [ ] Push notifications (browser)
- [ ] Offline caching / PWA manifest
- [ ] User-to-user messaging for review coordination
- [ ] Organization management by owners
- [ ] Rating system with 7 user statuses (Novice → Expert)

## Next Tasks
1. Real photo/video upload with storage
2. PWA manifest for mobile installation
3. Capacitor wrapping for AppStore/Google Play
4. Admin dashboard for moderation
