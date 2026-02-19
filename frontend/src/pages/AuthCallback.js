import React, { useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Loader2 } from 'lucide-react';

export default function AuthCallback() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const hasProcessed = useRef(false);

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const hash = location.hash;
    const sessionId = new URLSearchParams(hash.replace('#', '?')).get('session_id');

    if (!sessionId) {
      navigate('/login', { replace: true });
      return;
    }

    (async () => {
      try {
        const user = await login(sessionId);
        navigate('/dashboard', { replace: true, state: { user } });
      } catch (err) {
        console.error('Auth callback error:', err);
        navigate('/login', { replace: true });
      }
    })();
  }, [location, login, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto mb-4" />
        <p className="text-muted-foreground">Авторизация...</p>
      </div>
    </div>
  );
}
