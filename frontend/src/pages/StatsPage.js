import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Users, FileText, Building2, MapPin, Shield, Star, TrendingUp, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../lib/api';

const MOOD_CONFIG = {
  excellent: { name: 'Отличное', color: '#10b981', emoji: '5' },
  normal: { name: 'Нормальное', color: '#3b82f6', emoji: '4' },
  mild_upset: { name: 'Лёгкое расстройство', color: '#f59e0b', emoji: '3' },
  dissatisfaction: { name: 'Недовольство', color: '#f97316', emoji: '2' },
  stress: { name: 'Стресс', color: '#ef4444', emoji: '1' },
  anger: { name: 'Гнев', color: '#dc2626', emoji: '0' },
};

const MOOD_ORDER = ['anger', 'stress', 'dissatisfaction', 'mild_upset', 'normal', 'excellent'];

function AnimatedCounter({ target, duration = 2000, suffix = '' }) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const started = useRef(false);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !started.current) {
        started.current = true;
        const start = performance.now();
        const step = (now) => {
          const progress = Math.min((now - start) / duration, 1);
          const eased = 1 - Math.pow(1 - progress, 3);
          setCount(Math.round(eased * target));
          if (progress < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      }
    }, { threshold: 0.3 });
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [target, duration]);

  return <span ref={ref}>{count.toLocaleString('ru-RU')}{suffix}</span>;
}

function MoodGauge({ score, dominant, moodCounts, totalVotes }) {
  const pct = Math.min(Math.max((score / 5) * 100, 0), 100);
  const moodInfo = MOOD_CONFIG[dominant] || MOOD_CONFIG.normal;

  return (
    <div className="glass rounded-xl p-6" data-testid="mood-gauge">
      <h3 className="text-sm font-medium text-muted-foreground mb-4">Общий уровень настроения граждан</h3>
      <div className="flex items-center gap-4 mb-4">
        <div className="text-4xl font-bold" style={{ color: moodInfo.color }}>{score.toFixed(1)}</div>
        <div>
          <p className="text-lg font-semibold text-foreground">{moodInfo.name}</p>
          <p className="text-xs text-muted-foreground">{totalVotes} голосов</p>
        </div>
      </div>
      {/* Gauge bar */}
      <div className="relative h-4 rounded-full overflow-hidden mb-3" style={{ background: 'linear-gradient(to right, #dc2626, #ef4444, #f97316, #f59e0b, #3b82f6, #10b981)' }}>
        <div className="absolute top-0 h-full w-1 bg-white rounded shadow-lg transition-all duration-1000" style={{ left: `${pct}%` }} />
      </div>
      <div className="flex justify-between text-[9px] text-muted-foreground">
        <span>Гнев</span><span>Стресс</span><span>Недовольство</span><span>Расстройство</span><span>Нормальное</span><span>Отличное</span>
      </div>
      {/* Mood breakdown */}
      {totalVotes > 0 && (
        <div className="mt-4 space-y-1.5">
          {MOOD_ORDER.map(m => {
            const cnt = moodCounts[m] || 0;
            const p = totalVotes > 0 ? (cnt / totalVotes) * 100 : 0;
            return (
              <div key={m} className="flex items-center gap-2">
                <span className="text-[10px] text-muted-foreground w-28 text-right">{MOOD_CONFIG[m].name}</span>
                <div className="flex-1 bg-secondary/30 rounded-full h-2 overflow-hidden">
                  <div className="h-full rounded-full transition-all duration-700" style={{ width: `${p}%`, backgroundColor: MOOD_CONFIG[m].color }} />
                </div>
                <span className="text-[10px] text-muted-foreground w-8 text-right">{cnt}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function StatsPage() {
  const [stats, setStats] = useState(null);
  const [mood, setMood] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/stats/public').then(r => r.data),
      api.get('/stats/mood').then(r => r.data),
    ]).then(([s, m]) => { setStats(s); setMood(m); })
    .catch(() => {})
    .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="min-h-screen flex items-center justify-center"><div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" /></div>;
  if (!stats) return null;

  const LEVEL_NAMES = { yard: 'Дворовый', district: 'Районный', city: 'Городской', republic: 'Республ.', country: 'Народный' };
  const LEVEL_COLORS = { yard: '#10b981', district: '#3b82f6', city: '#8b5cf6', republic: '#f59e0b', country: '#ef4444' };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8" data-testid="stats-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight" style={{ fontFamily: 'Manrope' }}>Публичная статистика</h1>
          <p className="text-muted-foreground text-sm mt-1">Народный Контроль — в цифрах</p>
        </div>

        {/* Key metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
          {[
            { label: 'Граждане', value: stats.total_users, icon: Users, color: '#3b82f6' },
            { label: 'Отзывы', value: stats.total_reviews, icon: FileText, color: '#10b981' },
            { label: 'Организации', value: stats.total_orgs, icon: Building2, color: '#8b5cf6' },
            { label: 'Проблемы', value: stats.problems_on_map, icon: MapPin, color: '#f59e0b' },
          ].map(m => (
            <div key={m.label} className="glass rounded-xl p-4 text-center" data-testid={`stat-${m.label}`}>
              <m.icon className="w-5 h-5 mx-auto mb-2" style={{ color: m.color }} />
              <p className="text-2xl sm:text-3xl font-bold text-foreground">
                <AnimatedCounter target={m.value} />
              </p>
              <p className="text-[10px] text-muted-foreground mt-1">{m.label}</p>
            </div>
          ))}
        </div>

        {/* Mood gauge */}
        {mood && <div className="mb-6"><MoodGauge score={mood.average_score} dominant={mood.dominant_mood} moodCounts={mood.mood_counts} totalVotes={mood.total_votes} /></div>}

        {/* Councils by level */}
        <div className="glass rounded-xl p-6 mb-6">
          <h3 className="text-sm font-medium text-muted-foreground mb-4 flex items-center gap-2">
            <Shield className="w-4 h-4 text-primary" /> Советы по уровням
          </h3>
          <div className="grid grid-cols-5 gap-2">
            {Object.entries(stats.council_by_level || {}).map(([lvl, count]) => (
              <div key={lvl} className="text-center p-3 rounded-xl" style={{ backgroundColor: LEVEL_COLORS[lvl] + '15' }}>
                <p className="text-xl font-bold" style={{ color: LEVEL_COLORS[lvl] }}>
                  <AnimatedCounter target={count} duration={1200} />
                </p>
                <p className="text-[10px] text-muted-foreground mt-0.5">{LEVEL_NAMES[lvl]}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Review stats */}
        <div className="grid grid-cols-2 gap-3 mb-6">
          <div className="glass rounded-xl p-5">
            <h3 className="text-sm font-medium text-muted-foreground mb-3 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-green-400" /> Одобренные
            </h3>
            <p className="text-3xl font-bold text-green-400">
              <AnimatedCounter target={stats.approved_reviews} />
            </p>
            <p className="text-[10px] text-muted-foreground mt-1">из {stats.total_reviews} отзывов</p>
          </div>
          <div className="glass rounded-xl p-5">
            <h3 className="text-sm font-medium text-muted-foreground mb-3 flex items-center gap-2">
              <Shield className="w-4 h-4 text-blue-400" /> Верификаций
            </h3>
            <p className="text-3xl font-bold text-blue-400">
              <AnimatedCounter target={stats.total_verifications} />
            </p>
            <p className="text-[10px] text-muted-foreground mt-1">подтверждений отзывов</p>
          </div>
        </div>

        {/* Top organizations */}
        {stats.top_orgs?.length > 0 && (
          <div className="glass rounded-xl p-6">
            <h3 className="text-sm font-medium text-muted-foreground mb-4 flex items-center gap-2">
              <Star className="w-4 h-4 text-yellow-400" /> Рейтинг организаций
            </h3>
            <div className="space-y-2">
              {stats.top_orgs.map((org, i) => (
                <Link to={`/org/${org.org_id}`} key={org.org_id} className="flex items-center gap-3 p-3 rounded-xl hover:bg-secondary/30 transition-all" data-testid={`org-rank-${i}`}>
                  <span className="text-lg font-bold text-muted-foreground w-7 text-center">{i + 1}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-foreground truncate">{org.name}</p>
                    <p className="text-[10px] text-muted-foreground">{org.address} — {org.review_count} отзывов</p>
                  </div>
                  <div className="flex items-center gap-1">
                    <Star className="w-3.5 h-3.5 text-yellow-400 fill-yellow-400" />
                    <span className="text-sm font-bold text-foreground">{org.average_rating?.toFixed(1)}</span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                </Link>
              ))}
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}
