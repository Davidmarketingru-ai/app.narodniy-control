import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowLeft, Shield } from 'lucide-react';

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-3xl mx-auto px-4 py-8">
        <Link to="/login" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-6">
          <ArrowLeft className="w-4 h-4" /> Назад
        </Link>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center">
              <Shield className="w-5 h-5 text-primary" />
            </div>
            <h1 className="text-2xl font-bold text-foreground" style={{ fontFamily: 'Manrope' }}>Пользовательское соглашение</h1>
          </div>

          <div className="glass rounded-xl p-6 md:p-8 space-y-6 text-sm text-foreground leading-relaxed" data-testid="terms-content">
            <p className="text-xs text-muted-foreground">Последнее обновление: 2 апреля 2026 г.</p>

            <section>
              <h2 className="text-base font-bold mb-2">1. Общие положения</h2>
              <p>1.1. Настоящее Пользовательское соглашение (далее — «Соглашение») регулирует отношения между ОсОО «Народный Контроль», зарегистрированным в Парке Высоких Технологий Кыргызской Республики (далее — «Платформа»), и пользователем сети Интернет (далее — «Пользователь»).</p>
              <p className="mt-2">1.2. Использование Сервиса означает полное и безоговорочное принятие настоящего Соглашения.</p>
              <p className="mt-2">1.3. Сервис предназначен для лиц, достигших 16 лет.</p>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">2. Предмет соглашения</h2>
              <p>2.1. Платформа предоставляет доступ к системе гражданского контроля, включая: создание и верификацию отзывов об организациях и государственных служащих гражданских ведомств; участие в Народных Советах; голосования и обсуждения; получение информационных данных.</p>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">3. Ограничения контента</h2>
              <p>3.1. <strong>Категорически запрещается</strong> размещение любой информации, связанной с деятельностью или сотрудниками: органов государственной безопасности (ФСБ, ФСО, СВР); военной разведки (ГРУ); Министерства обороны и Генерального штаба; подразделений специального назначения; любых органов и лиц, деятельность которых связана с государственной тайной или имеет гриф секретности.</p>
              <p className="mt-2">3.2. Отзывы о государственных служащих разрешены исключительно в отношении гражданских ведомств: здравоохранение, образование, МФЦ, ЗАГС, ФНС, суды, участковые полиции, ГИБДД, ЖКХ, администрации.</p>
              <p className="mt-2">3.3. Запрещается: клевета (ст. 128.1 УК РФ); оскорбления (ст. 5.61 КоАП); экстремистские материалы (ст. 282 УК); разглашение персональных данных без согласия (152-ФЗ).</p>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">4. Верификация отзывов</h2>
              <p>4.1. Каждое подтверждение отзыва требует: минимум 1 фотографию-доказательство посещения; текстовый комментарий не менее 20 символов с описанием конкретного заведения.</p>
              <p className="mt-2">4.2. Подтверждения без фотографий или с нерелевантным текстом отклоняются системой автоматически.</p>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">5. Народные Советы</h2>
              <p>5.1. Система Народных Советов представляет собой иерархическую структуру гражданского самоуправления: Дворовый → Районный → Городской → Республиканский → Народный совет страны.</p>
              <p className="mt-2">5.2. Голосования в Советах носят рекомендательный характер и не имеют юридической силы.</p>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">6. Ответственность</h2>
              <p>6.1. Сервис предоставляется «как есть». Платформа не несёт ответственности за действия Пользователей.</p>
              <p className="mt-2">6.2. Пользователь несёт полную юридическую ответственность за размещаемый контент в соответствии с законодательством страны своего пребывания.</p>
            </section>

            <section>
              <h2 className="text-base font-bold mb-2">7. Разрешение споров</h2>
              <p>7.1. Споры разрешаются в соответствии с законодательством Кыргызской Республики.</p>
            </section>

            <section className="border-t border-border/50 pt-4">
              <h2 className="text-base font-bold mb-2">Реквизиты</h2>
              <p>ОсОО «Народный Контроль»<br/>Кыргызская Республика, г. Бишкек, Парк Высоких Технологий<br/>Email: support@narodkontrol.kg</p>
            </section>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
