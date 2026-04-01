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
            <p className="text-xs text-muted-foreground">Последнее обновление: 23 февраля 2026 г. | В соответствии с Федеральным законом № 152-ФЗ «О персональных данных»</p>

            <section>
              <h2 className="text-base font-bold mb-2">1. Общие положения</h2>
              <p>1.1. Настоящая Политика конфиденциальности (далее — «Политика») определяет порядок обработки и защиты персональных данных Пользователей сервиса «Народный Контроль».</p>
              <p className="mt-2">1.2. Оператор персональных данных: ООО «Народный Контроль» (ИНН: 0000000000, ОГРН: 0000000000000), адрес: 362000, РСО-Алания, г. Владикавказ, ул. Ленина, д. 1, оф. 100.</p>
              <p className="mt-2">1.3. Ответственный за организацию обработки персональных данных: Иванов Иван Иванович, email: dpo@narodkontrol.ru.</p>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">2. Какие данные мы собираем</h2>
              <p>2.1. <strong>При авторизации через Google:</strong> адрес электронной почты, имя, фотография профиля, уникальный идентификатор Google.</p>
              <p className="mt-2">2.2. <strong>При верификации личности (по желанию):</strong> номер телефона, хэш паспортных данных (серия, номер, дата рождения — хранятся только в виде криптографического хэша SHA-256), информация о банковской верификации (только факт верификации, без финансовых данных).</p>
              <p className="mt-2">2.3. <strong>Автоматически:</strong> данные о действиях в сервисе (отзывы, баллы, активность), IP-адрес и данные cookie-файлов, техническая информация браузера (User-Agent).</p>
              <p className="mt-2">2.4. <strong>При обращении в техподдержку:</strong> текст обращения и переписки.</p>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">3. Цели обработки</h2>
              <p>Персональные данные обрабатываются для:</p>
              <ul className="list-disc pl-5 space-y-1 mt-2">
                <li>Предоставления доступа к функциям Сервиса (ст. 6 ч. 1 п. 2 ФЗ-152)</li>
                <li>Идентификации и верификации Пользователя</li>
                <li>Обеспечения работы системы рейтингов и баллов</li>
                <li>Направления уведомлений о статусе отзывов</li>
                <li>Обработки обращений в техподдержку</li>
                <li>Улучшения качества Сервиса</li>
                <li>Соблюдения требований законодательства РФ</li>
              </ul>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">4. Правовые основания обработки</h2>
              <p>4.1. Согласие субъекта персональных данных (ст. 6 ч. 1 п. 1 ФЗ-152).</p>
              <p className="mt-2">4.2. Исполнение договора (Пользовательского соглашения) (ст. 6 ч. 1 п. 5 ФЗ-152).</p>
              <p className="mt-2">4.3. Выполнение требований законодательства РФ (ст. 6 ч. 1 п. 2 ФЗ-152).</p>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">5. Хранение и защита данных</h2>
              <p>5.1. Данные хранятся на серверах, расположенных на территории Российской Федерации, в соответствии с требованиями ч. 5 ст. 18 ФЗ-152.</p>
              <p className="mt-2">5.2. Применяемые меры защиты: шифрование данных при передаче (TLS/SSL); хэширование чувствительных данных (SHA-256); разграничение доступа на основе ролей; регулярное резервное копирование; журналирование действий с персональными данными.</p>
              <p className="mt-2">5.3. Сроки хранения: данные аккаунта — в течение действия аккаунта + 3 года после удаления; данные обращений — 5 лет; cookie-файлы — до 1 года.</p>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">6. Передача данных третьим лицам</h2>
              <p>6.1. Оператор не продаёт и не передаёт персональные данные третьим лицам, за исключением:</p>
              <ul className="list-disc pl-5 space-y-1 mt-2">
                <li>Google LLC — для авторизации (OAuth 2.0)</li>
                <li>По запросу уполномоченных государственных органов РФ в случаях, предусмотренных законодательством</li>
              </ul>
              <p className="mt-2">6.2. Трансграничная передача данных осуществляется с соблюдением требований ст. 12 ФЗ-152.</p>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">7. Права пользователя</h2>
              <p>В соответствии со ст. 14-17 ФЗ-152 вы имеете право:</p>
              <ul className="list-disc pl-5 space-y-1 mt-2">
                <li>Получить информацию об обработке своих персональных данных</li>
                <li>Требовать уточнения, блокирования или уничтожения данных</li>
                <li>Отозвать согласие на обработку персональных данных</li>
                <li>Обжаловать действия Оператора в Роскомнадзор (rkn.gov.ru)</li>
                <li>Потребовать удаления аккаунта и всех связанных данных</li>
              </ul>
              <p className="mt-2">Для реализации прав направьте обращение на dpo@narodkontrol.ru или через раздел «Техподдержка». Срок рассмотрения — 30 календарных дней (ст. 14 ч. 4 ФЗ-152).</p>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">8. Cookie-файлы</h2>
              <p>8.1. Сервис использует cookie-файлы для: обеспечения авторизации (session_token); запоминания настроек (тема, масштаб текста).</p>
              <p className="mt-2">8.2. Пользователь может управлять cookie через настройки браузера. Отключение cookie может ограничить функциональность Сервиса.</p>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">9. Изменение Политики</h2>
              <p>9.1. Оператор вправе изменять Политику. Актуальная версия всегда доступна по адресу /privacy.</p>
              <p className="mt-2">9.2. При существенных изменениях Пользователи уведомляются через систему уведомлений Сервиса.</p>
            </section>

            <section className="border-t border-border/50 pt-4">
              <h2 className="text-base font-bold mb-2">Контакты</h2>
              <p>ООО «Народный Контроль»<br/>Ответственный за обработку ПД: Иванов Иван Иванович<br/>Email: dpo@narodkontrol.ru<br/>Общий: support@narodkontrol.ru<br/>Тел.: +7 (800) 000-00-00<br/>Роскомнадзор: rkn.gov.ru</p>
            </section>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
