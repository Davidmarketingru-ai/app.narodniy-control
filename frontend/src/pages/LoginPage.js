import React, { useState } from 'react';
import { Shield, Check } from 'lucide-react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function LoginPage() {
  const [consentChecked, setConsentChecked] = useState(false);
  const [ageChecked, setAgeChecked] = useState(false);

  const canLogin = consentChecked && ageChecked;

  const handleGoogleLogin = () => {
    if (!canLogin) return;
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + '/dashboard';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background relative overflow-hidden" data-testid="login-page">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-emerald-500/5" />
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl" />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative z-10 w-full max-w-md mx-4"
      >
        <div className="glass rounded-2xl p-8 text-center">
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-primary/10 mb-6"
          >
            <Shield className="w-10 h-10 text-primary" />
          </motion.div>

          <h1 className="text-3xl font-bold text-foreground tracking-tight mb-2" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Народный Контроль
          </h1>
          <p className="text-muted-foreground mb-6 text-lg">
            Верифицированные отзывы для вашего города
          </p>

          {/* Consent checkboxes */}
          <div className="text-left space-y-3 mb-6">
            <label className="flex items-start gap-3 cursor-pointer group" data-testid="consent-checkbox-label">
              <div className="mt-0.5 shrink-0">
                <input type="checkbox" checked={consentChecked} onChange={e => setConsentChecked(e.target.checked)}
                  className="sr-only" data-testid="consent-checkbox" />
                <div className={`w-5 h-5 rounded-md border-2 flex items-center justify-center transition-all ${
                  consentChecked ? 'bg-primary border-primary' : 'border-muted-foreground/40 group-hover:border-primary/60'
                }`}>
                  {consentChecked && <Check className="w-3 h-3 text-primary-foreground" />}
                </div>
              </div>
              <span className="text-xs text-muted-foreground leading-relaxed">
                Я принимаю{' '}
                <Link to="/terms" className="text-primary hover:underline">Пользовательское соглашение</Link>
                {' '}и{' '}
                <Link to="/privacy" className="text-primary hover:underline">Политику конфиденциальности</Link>
                , даю согласие на обработку персональных данных в соответствии с ФЗ-152
              </span>
            </label>

            <label className="flex items-start gap-3 cursor-pointer group" data-testid="age-checkbox-label">
              <div className="mt-0.5 shrink-0">
                <input type="checkbox" checked={ageChecked} onChange={e => setAgeChecked(e.target.checked)}
                  className="sr-only" data-testid="age-checkbox" />
                <div className={`w-5 h-5 rounded-md border-2 flex items-center justify-center transition-all ${
                  ageChecked ? 'bg-primary border-primary' : 'border-muted-foreground/40 group-hover:border-primary/60'
                }`}>
                  {ageChecked && <Check className="w-3 h-3 text-primary-foreground" />}
                </div>
              </div>
              <span className="text-xs text-muted-foreground leading-relaxed">
                Мне исполнилось 16 лет (ФЗ-436 «О защите детей»)
              </span>
            </label>
          </div>

          <button
            onClick={handleGoogleLogin}
            disabled={!canLogin}
            data-testid="google-login-btn"
            className={`w-full flex items-center justify-center gap-3 font-medium py-4 px-6 rounded-xl border transition-all shadow-sm ${
              canLogin
                ? 'bg-white hover:bg-gray-50 text-gray-800 border-gray-200 hover:scale-[1.02] active:scale-[0.98] cursor-pointer'
                : 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed opacity-60'
            }`}
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            Войти через Google
          </button>

          <p className="text-[11px] text-muted-foreground mt-4">
            Сервис предназначен для лиц старше 16 лет (ФЗ-436)
          </p>

          <div className="flex items-center justify-center gap-3 mt-4 text-[11px] text-muted-foreground">
            <Link to="/terms" className="hover:text-foreground transition-colors">Соглашение</Link>
            <span>|</span>
            <Link to="/privacy" className="hover:text-foreground transition-colors">Конфиденциальность</Link>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
