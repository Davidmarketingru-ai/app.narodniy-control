import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Cookie, X } from 'lucide-react';
import { Link } from 'react-router-dom';

export function CookieBanner() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const accepted = localStorage.getItem('nk_cookies_accepted');
    if (!accepted) setVisible(true);
  }, []);

  const accept = () => {
    localStorage.setItem('nk_cookies_accepted', Date.now().toString());
    setVisible(false);
  };

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="fixed bottom-0 left-0 right-0 z-[100] p-4 md:p-6"
          data-testid="cookie-banner"
        >
          <div className="max-w-2xl mx-auto glass rounded-2xl p-5 border border-border/50 shadow-xl">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center shrink-0">
                <Cookie className="w-5 h-5 text-primary" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-foreground font-medium mb-1">Мы используем cookie-файлы</p>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Для корректной работы авторизации и сохранения ваших настроек сервис использует cookie-файлы.
                  Продолжая использовать сервис, вы соглашаетесь с{' '}
                  <Link to="/privacy" className="text-primary hover:underline">Политикой конфиденциальности</Link>.
                </p>
                <div className="flex gap-2 mt-3">
                  <button onClick={accept} data-testid="cookie-accept-btn"
                    className="bg-primary text-primary-foreground px-5 py-2 rounded-xl text-xs font-medium hover:bg-primary/90 transition-all">
                    Принять
                  </button>
                  <Link to="/privacy" className="text-xs text-muted-foreground hover:text-foreground px-3 py-2 transition-colors">
                    Подробнее
                  </Link>
                </div>
              </div>
              <button onClick={accept} className="text-muted-foreground hover:text-foreground shrink-0">
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
