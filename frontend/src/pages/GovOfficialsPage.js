import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Building2, Star, Search, Plus, X, Loader2, ChevronRight, AlertTriangle,
  Send, User, Filter, ShieldAlert
} from 'lucide-react';
import api from '../lib/api';

const GOV_CATEGORY_ICONS = {
  healthcare: { label: 'Здравоохранение', color: '#ef4444' },
  education: { label: 'Образование', color: '#3b82f6' },
  mfc: { label: 'МФЦ', color: '#8b5cf6' },
  zags: { label: 'ЗАГС', color: '#ec4899' },
  tax: { label: 'ФНС', color: '#f97316' },
  court: { label: 'Суды', color: '#6b7280' },
  police_local: { label: 'Участковые', color: '#0ea5e9' },
  gibdd: { label: 'ГИБДД', color: '#eab308' },
  housing: { label: 'ЖКХ', color: '#10b981' },
  administration: { label: 'Администрация', color: '#6366f1' },
  social: { label: 'Соцзащита', color: '#14b8a6' },
  pension: { label: 'Пенсионный фонд', color: '#f59e0b' },
  employment: { label: 'Занятость', color: '#84cc16' },
  transport: { label: 'Транспорт', color: '#64748b' },
  ecology: { label: 'Экология', color: '#22c55e' },
};

const REVIEW_CATS = [
  { id: 'service_quality', label: 'Качество обслуживания' },
  { id: 'competence', label: 'Компетентность' },
  { id: 'corruption', label: 'Коррупция / Взятки' },
  { id: 'rudeness', label: 'Грубость' },
  { id: 'efficiency', label: 'Эффективность' },
  { id: 'positive', label: 'Благодарность' },
];

export default function GovOfficialsPage() {
  const [categories, setCategories] = useState({});
  const [officials, setOfficials] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCat, setSelectedCat] = useState('');
  const [selectedOfficial, setSelectedOfficial] = useState(null);
  const [showAddOfficial, setShowAddOfficial] = useState(false);
  const [showAddReview, setShowAddReview] = useState(false);
  const [search, setSearch] = useState('');
  const [form, setForm] = useState({ name: '', position: '', department: '', gov_category: '', region: '' });
  const [reviewForm, setReviewForm] = useState({ title: '', content: '', rating: 3, category: 'service_quality' });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get('/gov/categories').then(r => r.data),
      api.get('/gov/officials').then(r => r.data),
    ]).then(([cats, offs]) => { setCategories(cats); setOfficials(offs); }).finally(() => setLoading(false));
  }, []);

  const loadOfficials = async () => {
    const params = {};
    if (selectedCat) params.category = selectedCat;
    if (search) params.q = search;
    const res = await api.get('/gov/officials', { params });
    setOfficials(res.data);
  };

  useEffect(() => { if (!loading) loadOfficials(); }, [selectedCat, search]);

  const openOfficial = async (off) => {
    setSelectedOfficial(off);
    const res = await api.get('/gov/reviews', { params: { official_id: off.official_id } });
    setReviews(res.data);
  };

  const handleAddOfficial = async () => {
    if (!form.name || !form.position || !form.department || !form.gov_category) return;
    setSubmitting(true);
    try {
      const res = await api.post('/gov/officials', form);
      setOfficials(prev => [res.data, ...prev]);
      setShowAddOfficial(false);
      setForm({ name: '', position: '', department: '', gov_category: '', region: '' });
    } catch (e) {
      alert(e.response?.data?.detail || 'Ошибка');
    } finally { setSubmitting(false); }
  };

  const handleAddReview = async () => {
    if (!reviewForm.title || !reviewForm.content || !selectedOfficial) return;
    setSubmitting(true);
    try {
      await api.post('/gov/reviews', { ...reviewForm, official_id: selectedOfficial.official_id });
      const res = await api.get('/gov/reviews', { params: { official_id: selectedOfficial.official_id } });
      setReviews(res.data);
      const off = await api.get(`/gov/officials/${selectedOfficial.official_id}`);
      setSelectedOfficial(off.data);
      setShowAddReview(false);
      setReviewForm({ title: '', content: '', rating: 3, category: 'service_quality' });
    } catch (e) {
      alert(e.response?.data?.detail || 'Ошибка');
    } finally { setSubmitting(false); }
  };

  if (selectedOfficial) {
    const cfg = GOV_CATEGORY_ICONS[selectedOfficial.gov_category] || { label: '?', color: '#6b7280' };
    return (
      <div className="max-w-3xl mx-auto" data-testid="gov-official-detail">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <button onClick={() => setSelectedOfficial(null)} className="flex items-center gap-2 text-sm text-muted-foreground mb-4 hover:text-foreground">
            <X className="w-4 h-4" /> Назад
          </button>
          <div className="glass rounded-xl p-6 mb-4">
            <div className="flex items-start gap-4">
              <div className="w-14 h-14 rounded-xl flex items-center justify-center shrink-0" style={{ backgroundColor: cfg.color + '20' }}>
                <Building2 className="w-7 h-7" style={{ color: cfg.color }} />
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-bold text-foreground">{selectedOfficial.name}</h2>
                <p className="text-sm text-muted-foreground">{selectedOfficial.position}</p>
                <p className="text-xs text-muted-foreground mt-1">{selectedOfficial.department}</p>
                <div className="flex items-center gap-3 mt-2">
                  <span className="text-xs px-2 py-0.5 rounded-full text-white" style={{ backgroundColor: cfg.color }}>{cfg.label}</span>
                  <div className="flex items-center gap-1">
                    <Star className="w-3.5 h-3.5 text-yellow-400 fill-yellow-400" />
                    <span className="text-sm font-bold text-foreground">{selectedOfficial.average_rating}</span>
                    <span className="text-xs text-muted-foreground">({selectedOfficial.review_count})</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-foreground">Отзывы</h3>
            <button onClick={() => setShowAddReview(true)} data-testid="add-gov-review-btn"
              className="bg-primary text-primary-foreground px-4 py-2 rounded-xl text-sm flex items-center gap-2">
              <Plus className="w-4 h-4" /> Отзыв
            </button>
          </div>

          {/* Disclaimer */}
          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-3 mb-4 flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-yellow-400 shrink-0 mt-0.5" />
            <p className="text-[11px] text-muted-foreground">
              Отзывы носят субъективный характер. За клевету (ст. 128.1 УК РФ) и оскорбления (ст. 5.61 КоАП) предусмотрена ответственность. Платформа не проверяет достоверность отзывов.
            </p>
          </div>

          {reviews.length === 0 ? (
            <div className="glass rounded-xl p-8 text-center">
              <p className="text-muted-foreground">Отзывов пока нет. Будьте первым!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {reviews.map(r => {
                const rc = REVIEW_CATS.find(c => c.id === r.category);
                return (
                  <div key={r.review_id} className="glass rounded-xl p-4" data-testid={`gov-review-${r.review_id}`}>
                    <div className="flex items-center gap-2 mb-2">
                      <div className="flex">{[1,2,3,4,5].map(s => <Star key={s} className={`w-3.5 h-3.5 ${s <= r.rating ? 'text-yellow-400 fill-yellow-400' : 'text-muted-foreground/20'}`} />)}</div>
                      {rc && <span className="text-[10px] px-1.5 py-0.5 rounded bg-secondary text-muted-foreground">{rc.label}</span>}
                    </div>
                    <h4 className="font-medium text-foreground text-sm">{r.title}</h4>
                    <p className="text-sm text-muted-foreground mt-1">{r.content}</p>
                    <p className="text-[10px] text-muted-foreground mt-2 font-mono">{r.user_name} — {new Date(r.created_at).toLocaleDateString('ru-RU')}</p>
                  </div>
                );
              })}
            </div>
          )}

          {/* Add Review Modal */}
          <AnimatePresence>
            {showAddReview && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowAddReview(false)}>
                <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
                  onClick={e => e.stopPropagation()} className="glass rounded-2xl p-6 w-full max-w-lg" data-testid="add-gov-review-modal">
                  <h2 className="text-lg font-bold mb-4">Отзыв о {selectedOfficial.name}</h2>
                  <div className="space-y-3">
                    <select value={reviewForm.category} onChange={e => setReviewForm(p => ({ ...p, category: e.target.value }))}
                      className="w-full bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none">
                      {REVIEW_CATS.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
                    </select>
                    <div className="flex gap-1">
                      {[1,2,3,4,5].map(s => (
                        <button key={s} onClick={() => setReviewForm(p => ({ ...p, rating: s }))}
                          className="p-1"><Star className={`w-6 h-6 ${s <= reviewForm.rating ? 'text-yellow-400 fill-yellow-400' : 'text-muted-foreground/30'}`} /></button>
                      ))}
                    </div>
                    <input type="text" value={reviewForm.title} onChange={e => setReviewForm(p => ({ ...p, title: e.target.value }))}
                      placeholder="Заголовок" className="w-full bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" data-testid="gov-review-title" />
                    <textarea value={reviewForm.content} onChange={e => setReviewForm(p => ({ ...p, content: e.target.value }))}
                      placeholder="Опишите ваш опыт (мин. 20 символов)..." rows={3}
                      className="w-full bg-secondary/50 rounded-xl p-3 text-sm text-foreground outline-none resize-none" data-testid="gov-review-content" />
                    <button onClick={handleAddReview} disabled={submitting} data-testid="submit-gov-review"
                      className="w-full bg-primary text-primary-foreground py-3 rounded-xl font-medium disabled:opacity-50 flex items-center justify-center gap-2">
                      {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Send className="w-4 h-4" /> Отправить</>}
                    </button>
                  </div>
                </motion.div>
              </div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto" data-testid="gov-officials-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight" style={{ fontFamily: 'Manrope' }}>Госслужащие</h1>
            <p className="text-muted-foreground text-sm mt-1">Отзывы о работе гражданских ведомств</p>
          </div>
          <button onClick={() => setShowAddOfficial(true)} data-testid="add-official-btn"
            className="bg-primary text-primary-foreground px-4 py-2.5 rounded-xl text-sm font-medium flex items-center gap-2">
            <Plus className="w-4 h-4" /> Добавить
          </button>
        </div>

        {/* Security notice */}
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-6 flex items-start gap-3" data-testid="security-notice">
          <ShieldAlert className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm text-foreground font-medium">Ограничение по безопасности</p>
            <p className="text-xs text-muted-foreground mt-1">
              Отзывы о сотрудниках ФСБ, ФСО, СВР, ГРУ, Минобороны, спецназа и других силовых/секретных структур 
              <strong className="text-red-400"> строго запрещены</strong>. Нарушение влечёт блокировку аккаунта.
            </p>
          </div>
        </div>

        {/* Search + Filter */}
        <div className="flex gap-2 mb-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input type="text" value={search} onChange={e => setSearch(e.target.value)}
              placeholder="Поиск по имени или ведомству..." data-testid="gov-search"
              className="w-full bg-secondary/50 rounded-xl h-11 pl-10 pr-4 text-sm text-foreground placeholder:text-muted-foreground outline-none" />
          </div>
        </div>

        {/* Category filter */}
        <div className="flex gap-2 overflow-x-auto pb-2 mb-4 scrollbar-hide">
          <button onClick={() => setSelectedCat('')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap shrink-0 ${!selectedCat ? 'bg-primary text-primary-foreground' : 'glass text-muted-foreground'}`}>
            Все
          </button>
          {Object.entries(GOV_CATEGORY_ICONS).map(([key, cfg]) => (
            <button key={key} onClick={() => setSelectedCat(key)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap shrink-0 ${selectedCat === key ? 'text-white' : 'glass text-muted-foreground'}`}
              style={selectedCat === key ? { backgroundColor: cfg.color } : {}}>
              {cfg.label}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
        ) : officials.length === 0 ? (
          <div className="glass rounded-xl p-8 text-center">
            <Building2 className="w-12 h-12 text-muted-foreground/20 mx-auto mb-3" />
            <p className="text-muted-foreground">Служащих не найдено. Добавьте первого!</p>
          </div>
        ) : (
          <div className="space-y-2">
            {officials.map(off => {
              const cfg = GOV_CATEGORY_ICONS[off.gov_category] || { label: '?', color: '#6b7280' };
              return (
                <button key={off.official_id} onClick={() => openOfficial(off)}
                  className="w-full glass rounded-xl p-4 text-left hover:border-primary/30 transition-all flex items-center gap-4"
                  data-testid={`official-${off.official_id}`}>
                  <div className="w-11 h-11 rounded-xl flex items-center justify-center shrink-0" style={{ backgroundColor: cfg.color + '20' }}>
                    <Building2 className="w-5 h-5" style={{ color: cfg.color }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-foreground truncate">{off.name}</p>
                    <p className="text-xs text-muted-foreground truncate">{off.position} — {off.department}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-[10px] px-1.5 py-0.5 rounded text-white" style={{ backgroundColor: cfg.color }}>{cfg.label}</span>
                      <div className="flex items-center gap-0.5">
                        <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                        <span className="text-xs font-mono text-foreground">{off.average_rating}</span>
                      </div>
                      <span className="text-[10px] text-muted-foreground">{off.review_count} отз.</span>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground shrink-0" />
                </button>
              );
            })}
          </div>
        )}

        {/* Add Official Modal */}
        <AnimatePresence>
          {showAddOfficial && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowAddOfficial(false)}>
              <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
                onClick={e => e.stopPropagation()} className="glass rounded-2xl p-6 w-full max-w-lg" data-testid="add-official-modal">
                <h2 className="text-lg font-bold mb-4">Добавить госслужащего</h2>
                <div className="space-y-3">
                  <select value={form.gov_category} onChange={e => setForm(p => ({ ...p, gov_category: e.target.value }))} data-testid="official-category-select"
                    className="w-full bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none">
                    <option value="">Выберите категорию</option>
                    {Object.entries(GOV_CATEGORY_ICONS).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
                  </select>
                  <input type="text" value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))}
                    placeholder="ФИО служащего" className="w-full bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" data-testid="official-name" />
                  <input type="text" value={form.position} onChange={e => setForm(p => ({ ...p, position: e.target.value }))}
                    placeholder="Должность" className="w-full bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" data-testid="official-position" />
                  <input type="text" value={form.department} onChange={e => setForm(p => ({ ...p, department: e.target.value }))}
                    placeholder="Ведомство / Учреждение" className="w-full bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" data-testid="official-department" />
                  <button onClick={handleAddOfficial} disabled={submitting || !form.gov_category || !form.name} data-testid="submit-official"
                    className="w-full bg-primary text-primary-foreground py-3 rounded-xl font-medium disabled:opacity-50 flex items-center justify-center gap-2">
                    {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Plus className="w-4 h-4" /> Добавить</>}
                  </button>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
