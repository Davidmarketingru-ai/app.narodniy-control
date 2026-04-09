import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import AppLayout from './components/AppLayout';
import { CookieBanner } from './components/CookieBanner';
import LoginPage from './pages/LoginPage';
import AuthCallback from './pages/AuthCallback';
import DashboardPage from './pages/DashboardPage';
import CreateReviewPage from './pages/CreateReviewPage';
import MapPage from './pages/MapPage';
import ProfilePage from './pages/ProfilePage';
import RewardsPage from './pages/RewardsPage';
import NotificationsPage from './pages/NotificationsPage';
import ReviewDetailPage from './pages/ReviewDetailPage';
import AdminPage from './pages/AdminPage';
import NewsPage from './pages/NewsPage';
import WidgetsPage from './pages/WidgetsPage';
import ProblemsMapPage from './pages/ProblemsMapPage';
import VerificationPage from './pages/VerificationPage';
import SupportPage from './pages/SupportPage';
import TermsPage from './pages/TermsPage';
import PrivacyPage from './pages/PrivacyPage';
import VerifyFeedPage from './pages/VerifyFeedPage';
import GovOfficialsPage from './pages/GovOfficialsPage';
import CouncilsPage from './pages/CouncilsPage';
import StatsPage from './pages/StatsPage';
import PublicOrgPage from './pages/PublicOrgPage';
import { Loader2 } from 'lucide-react';

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <AppLayout>{children}</AppLayout>;
}

function AppRouter() {
  useLocation();

  // Backward compatibility: if session_id is in hash on ANY page, redirect to callback
  if (window.location.hash?.includes('session_id=') && !window.location.pathname.startsWith('/auth/callback')) {
    const hash = window.location.hash;
    window.location.replace('/auth/callback' + hash);
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/auth/callback" element={<AuthCallback />} />
      <Route path="/terms" element={<TermsPage />} />
      <Route path="/privacy" element={<PrivacyPage />} />
      <Route path="/stats" element={<StatsPage />} />
      <Route path="/org/:orgId" element={<PublicOrgPage />} />
      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/create" element={<ProtectedRoute><CreateReviewPage /></ProtectedRoute>} />
      <Route path="/map" element={<ProtectedRoute><MapPage /></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
      <Route path="/rewards" element={<ProtectedRoute><RewardsPage /></ProtectedRoute>} />
      <Route path="/notifications" element={<ProtectedRoute><NotificationsPage /></ProtectedRoute>} />
      <Route path="/reviews/:reviewId" element={<ProtectedRoute><ReviewDetailPage /></ProtectedRoute>} />
      <Route path="/admin" element={<ProtectedRoute><AdminPage /></ProtectedRoute>} />
      <Route path="/news" element={<ProtectedRoute><NewsPage /></ProtectedRoute>} />
      <Route path="/widgets" element={<ProtectedRoute><WidgetsPage /></ProtectedRoute>} />
      <Route path="/problems-map" element={<ProtectedRoute><ProblemsMapPage /></ProtectedRoute>} />
      <Route path="/verification" element={<ProtectedRoute><VerificationPage /></ProtectedRoute>} />
      <Route path="/support" element={<ProtectedRoute><SupportPage /></ProtectedRoute>} />
      <Route path="/verify" element={<ProtectedRoute><VerifyFeedPage /></ProtectedRoute>} />
      <Route path="/gov" element={<ProtectedRoute><GovOfficialsPage /></ProtectedRoute>} />
      <Route path="/councils" element={<ProtectedRoute><CouncilsPage /></ProtectedRoute>} />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <AppRouter />
          <CookieBanner />
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
