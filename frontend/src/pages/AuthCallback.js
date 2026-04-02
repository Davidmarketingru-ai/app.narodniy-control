import React, { useEffect, useRef, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Loader2, AlertCircle, RefreshCw } from 'lucide-react';

export default function AuthCallback() {
  const { login } = useAuth();
  const hasProcessed = useRef(false);
  const [error, setError] = useState('');
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const extractSessionId = () => {
      // 1. Try hash fragment (standard flow)
      const hash = window.location.hash;
      if (hash) {
        const hashParams = new URLSearchParams(hash.substring(1));
        const fromHash = hashParams.get('session_id');
        if (fromHash) {
          console.log('AuthCallback: session_id from hash');
          return fromHash;
        }
      }

      // 2. Try query params (mobile fallback — some redirects convert hash to query)
      const searchParams = new URLSearchParams(window.location.search);
      const fromQuery = searchParams.get('session_id');
      if (fromQuery) {
        console.log('AuthCallback: session_id from query params');
        return fromQuery;
      }

      // 3. Try full URL scan (handle edge cases with encoding)
      const fullUrl = window.location.href;
      const sessionMatch = fullUrl.match(/[#?&]session_id=([^&#]+)/);
      if (sessionMatch) {
        console.log('AuthCallback: session_id from URL regex');
        return decodeURIComponent(sessionMatch[1]);
      }

      // 4. Try sessionStorage (set before redirect as safety net)
      const stored = sessionStorage.getItem('nk_pending_session_id');
      if (stored) {
        sessionStorage.removeItem('nk_pending_session_id');
        console.log('AuthCallback: session_id from sessionStorage');
        return stored;
      }

      return null;
    };

    const processAuth = async () => {
      const sessionId = extractSessionId();

      if (!sessionId) {
        console.error('AuthCallback: No session_id found. URL:', window.location.href);
        setError('Не удалось получить данные авторизации. Попробуйте ещё раз.');
        return;
      }

      try {
        console.log('AuthCallback: Processing login...');
        await login(sessionId);
        console.log('AuthCallback: Login successful');
        // Clean up URL hash/params before redirecting
        window.location.replace('/dashboard');
      } catch (err) {
        console.error('AuthCallback: Login error:', err?.response?.status, err?.response?.data || err?.message);
        const detail = err?.response?.data?.detail || 'Ошибка авторизации';
        setError(detail);
      }
    };

    processAuth();
  }, [login]);

  const handleRetry = () => {
    setError('');
    setRetryCount(prev => prev + 1);
    window.location.href = '/login';
  };

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background" data-testid="auth-error">
        <div className="text-center max-w-md mx-4 glass rounded-2xl p-8">
          <AlertCircle className="w-12 h-12 text-destructive mx-auto mb-4" />
          <p className="text-foreground font-semibold text-lg mb-2">Ошибка авторизации</p>
          <p className="text-sm text-muted-foreground mb-6">{error}</p>
          <button
            onClick={handleRetry}
            data-testid="auth-retry-btn"
            className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded-xl font-medium hover:bg-primary/90 transition-all"
          >
            <RefreshCw className="w-4 h-4" />
            Попробовать снова
          </button>
          <p className="text-[11px] text-muted-foreground mt-4">
            Если проблема повторяется, попробуйте открыть приложение напрямую в браузере (не через мессенджер)
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background" data-testid="auth-processing">
      <div className="text-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto mb-4" />
        <p className="text-foreground font-medium">Авторизация...</p>
        <p className="text-xs text-muted-foreground mt-2">Подключаемся к аккаунту Google</p>
      </div>
    </div>
  );
}
