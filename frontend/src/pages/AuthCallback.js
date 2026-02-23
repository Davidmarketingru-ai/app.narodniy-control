import React, { useEffect, useRef, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Loader2, AlertCircle } from 'lucide-react';

export default function AuthCallback() {
  const { login } = useAuth();
  const hasProcessed = useRef(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    // Use window.location.hash directly for maximum reliability
    const hash = window.location.hash;
    console.log('AuthCallback: Raw hash:', hash);

    const params = new URLSearchParams(hash.substring(1)); // Remove the leading #
    const sessionId = params.get('session_id');

    console.log('AuthCallback: Extracted session_id:', sessionId ? sessionId.substring(0, 10) + '...' : 'null');

    if (!sessionId) {
      console.error('AuthCallback: No session_id found in hash:', hash);
      setError('Не удалось получить session_id. Попробуйте ещё раз.');
      setTimeout(() => { window.location.href = '/login'; }, 3000);
      return;
    }

    (async () => {
      try {
        console.log('AuthCallback: Calling login with session_id...');
        await login(sessionId);
        console.log('AuthCallback: Login successful, redirecting...');
        // Use hard redirect for maximum reliability — ensures cookie is picked up on fresh page load
        window.location.href = '/dashboard';
      } catch (err) {
        console.error('AuthCallback: Login error:', err?.response?.status, err?.response?.data || err?.message);
        const detail = err?.response?.data?.detail || 'Ошибка авторизации. Попробуйте снова.';
        setError(detail);
        setTimeout(() => { window.location.href = '/login'; }, 3000);
      }
    })();
  }, [login]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center max-w-md mx-4">
          <AlertCircle className="w-10 h-10 text-destructive mx-auto mb-4" />
          <p className="text-foreground font-medium mb-2">Ошибка авторизации</p>
          <p className="text-sm text-muted-foreground mb-4">{error}</p>
          <p className="text-xs text-muted-foreground">Перенаправление на страницу входа...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto mb-4" />
        <p className="text-muted-foreground">Авторизация...</p>
      </div>
    </div>
  );
}
