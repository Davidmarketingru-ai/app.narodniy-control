import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowLeft, Lock } from 'lucide-react';

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-3xl mx-auto px-4 py-8">
        <Link to="/login" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-6">
          <ArrowLeft className="w-4 h-4" /> Назад
        </Link>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center">
              <Lock className="w-5 h-5 text-emerald-400" />
            </div>
            <h1 className="text-2xl font-bold text-foreground" style={{ fontFamily: 'Manrope' }}>Политика конфиденциальности</h1>
          </div>

          <div className="glass rounded-xl p-6 md:p-8 space-y-6 text-sm text-foreground leading-relaxed" data-testid="privacy-content">
            <p className="text-xs text-muted-foreground">Последнее обновление: 2 апреля 2026 г.</p>

            <section>
              <h2 className="text-base font-bold mb-2">1. Оператор данных</h2>
              <p>Оператор: ОсОО «Народный Контроль», зарегистрированное в Парке Высоких Технологий Кыргызской Республики, г. Бишкек. Контакт: privacy@narodkontrol.kg.</p>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">2. Собираемые данные</h2>
              <p>При авторизации: email, имя, фото профиля (Google OAuth). При верификации: номер телефона, хэш паспортных данных (SHA-256). Автоматически: IP-адрес, cookie, данные активности.</p>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">3. Цели обработки</h2>
              <p>Идентификация пользователя, работа системы рейтингов, обработка обращений, улучшение сервиса, соблюдение законодательства.</p>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">4. Хранение</h2>
              <p>Данные хранятся на защищённых серверах. Применяется шифрование TLS/SSL, хэширование SHA-256, разграничение доступа по ролям.</p>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">5. Передача третьим лицам</h2>
              <p>Данные не продаются. Передача: Google LLC (авторизация); государственным органам по законному запросу.</p>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">6. Права пользователя</h2>
              <p>Вы вправе: получить информацию об обработке данных; требовать удаления; отозвать согласие. Обращения: privacy@narodkontrol.kg или раздел «Поддержка». Срок: 30 дней.</p>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">7. Cookie</h2>
              <p>Используются для авторизации (session_token) и настроек. Управление — через браузер.</p>
            </section>

            <section className="border-t border-border/50 pt-4">
              <p>ОсОО «Народный Контроль»<br/>Кыргызская Республика, г. Бишкек, ПВТ<br/>privacy@narodkontrol.kg</p>
            </section>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
