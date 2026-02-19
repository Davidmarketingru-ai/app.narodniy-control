import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  User, Shield, Award, Settings, LogOut, Sun, Moon, ChevronRight,
  Copy, Check, Sprout, Eye, ShieldCheck, Crown, Star, Flame,
  Users, Gift, Loader2
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { profileApi, ratingApi, referralApi } from '../lib/api';
import { useNavigate, Link } from 'react-router-dom';

const statusIcons = {
  seedling: Sprout, eye: Eye, shield: Shield, 'shield-check': ShieldCheck,
  award: Award, crown: Crown, star: Star,
};

export default function ProfilePage() {
  const { user, logout, refreshUser } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [textScale, setTextScale] = useState(user?.text_scale || 1);
  const [showScaleSettings, setShowScaleSettings] = useState(false);
  const [ratingStatus, setRatingStatus] = useState(null);
  const [referralStats, setReferralStats] = useState(null);
  const [referralCode, setReferralCode] = useState('');
  const [referralApplying, setReferralApplying] = useState(false);
  const [referralMsg, setReferralMsg] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    ratingApi.status().then(setRatingStatus).catch(console.error);
    referralApi.stats().then(setReferralStats).catch(console.error);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleScaleChange = async (newScale) => {
    setTextScale(newScale);
    try { await profileApi.update({ text_scale: newScale }); await refreshUser(); } catch {}
  };

  const handleAgeGroupChange = async (ageGroup) => {
    try { await profileApi.update({ age_group: ageGroup }); await refreshUser(); } catch {}
  };

  const handleCopyReferral = () => {
    navigator.clipboard.writeText(referralStats?.referral_code || user?.referral_code || '');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleApplyReferral = async () => {
    if (!referralCode.trim()) return;
    setReferralApplying(true);
    setReferralMsg('');
    try {
      const res = await referralApi.apply(referralCode);
      setReferralMsg(res.message);
      await refreshUser();
    } catch (err) {
      setReferralMsg(err.response?.data?.detail || 'Ошибка');
    } finally {
      setReferralApplying(false);
    }
  };

  const ageGroups = [
    { value: '18-25', label: '18-25 лет' },
    { value: '26-40', label: '26-40 лет' },
    { value: '41-60', label: '41-60 лет' },
    { value: '60+', label: '60+ лет' },
  ];

  const StatusIcon = ratingStatus ? statusIcons[ratingStatus.current.icon] || Star : Star;

  return (
    <div className="max-w-2xl mx-auto space-y-6" data-testid="profile-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold tracking-tight mb-6" style={{ fontFamily: 'Manrope' }}>
          Профиль
        </h1>

        {/* User Card */}
        <div className="glass rounded-xl p-6 mb-6">
          <div className="flex items-center gap-4 mb-4">
            {user?.picture ? (
              <img src={user.picture} alt="" className="w-16 h-16 rounded-full object-cover border-2 border-primary/30" />
            ) : (
              <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
                <User className="w-8 h-8 text-primary" />
              </div>
            )}
            <div>
              <h2 className="text-xl font-semibold text-foreground">{user?.name || 'Пользователь'}</h2>
              <p className="text-sm text-muted-foreground">{user?.email}</p>
              {user?.role === 'admin' && (
                <Link to="/admin" className="inline-flex items-center gap-1 mt-1 text-xs text-primary hover:underline">
                  <Shield className="w-3 h-3" /> Админ-панель
                </Link>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2 pt-4 border-t border-border/50">
            {user?.is_verified ? (
              <div className="flex items-center gap-2 text-emerald-400">
                <Shield className="w-4 h-4" /><span className="text-sm font-medium">Верифицирован</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-yellow-400">
                <Shield className="w-4 h-4" /><span className="text-sm font-medium">Не верифицирован</span>
              </div>
            )}
          </div>
        </div>

        {/* Rating Status */}
        {ratingStatus && (
          <div className="glass rounded-xl p-6 mb-6" data-testid="rating-status-card">
            <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
              <Award className="w-5 h-5 text-primary" />
              Рейтинг и статус
            </h3>
            <div className="flex items-center gap-4 mb-4">
              <div
                className="w-16 h-16 rounded-2xl flex items-center justify-center"
                style={{ backgroundColor: ratingStatus.current.color + '20' }}
              >
                <StatusIcon className="w-8 h-8" style={{ color: ratingStatus.current.color }} />
              </div>
              <div>
                <p className="text-xl font-bold" style={{ color: ratingStatus.current.color }}>
                  {ratingStatus.current.name}
                </p>
                <p className="text-sm text-muted-foreground">
                  Уровень {ratingStatus.level} из {ratingStatus.all_statuses.length}
                </p>
              </div>
            </div>

            {/* Progress to next */}
            {ratingStatus.next && (
              <div className="mb-4">
                <div className="flex justify-between text-xs text-muted-foreground mb-1">
                  <span>{ratingStatus.current.name}</span>
                  <span>{ratingStatus.next.name} ({ratingStatus.next.min_points} б.)</span>
                </div>
                <div className="w-full bg-secondary rounded-full h-2.5">
                  <div
                    className="rounded-full h-2.5 transition-all duration-500"
                    style={{ width: `${Math.min(ratingStatus.progress, 100)}%`, backgroundColor: ratingStatus.current.color }}
                  />
                </div>
              </div>
            )}

            {/* Stats */}
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-secondary/50 rounded-lg p-3 text-center">
                <p className="text-lg font-bold text-primary font-mono">{ratingStatus.points}</p>
                <p className="text-xs text-muted-foreground">Баллов</p>
              </div>
              <div className="bg-secondary/50 rounded-lg p-3 text-center">
                <p className="text-lg font-bold text-foreground font-mono">{ratingStatus.reviews_count}</p>
                <p className="text-xs text-muted-foreground">Отзывов</p>
              </div>
              <div className="bg-secondary/50 rounded-lg p-3 text-center">
                <p className="text-lg font-bold text-foreground font-mono">{ratingStatus.verifications_count}</p>
                <p className="text-xs text-muted-foreground">Подтв.</p>
              </div>
            </div>

            {/* All Statuses */}
            <div className="mt-4 grid grid-cols-7 gap-1">
              {ratingStatus.all_statuses.map((s, i) => {
                const unlocked = ratingStatus.points >= s.min_points;
                const SIcon = statusIcons[s.icon] || Star;
                return (
                  <div
                    key={s.name}
                    className={`flex flex-col items-center p-2 rounded-lg transition-all ${unlocked ? '' : 'opacity-30'}`}
                    title={`${s.name} (${s.min_points} б.)`}
                  >
                    <SIcon className="w-5 h-5 mb-1" style={{ color: s.color }} />
                    <span className="text-[9px] text-muted-foreground text-center leading-tight">{s.name}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Referral System */}
        <div className="glass rounded-xl p-6 mb-6" data-testid="referral-card">
          <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
            <Users className="w-5 h-5 text-primary" />
            Реферальная программа
          </h3>

          {/* Your referral code */}
          <div className="bg-primary/10 border border-primary/20 rounded-xl p-4 mb-4">
            <p className="text-xs text-muted-foreground uppercase tracking-wider mb-2">Ваш реферальный код</p>
            <div className="flex items-center gap-2">
              <code className="text-2xl font-bold text-primary font-mono tracking-widest" data-testid="user-referral-code">
                {referralStats?.referral_code || user?.referral_code || '—'}
              </code>
              <button
                onClick={handleCopyReferral}
                data-testid="copy-referral-btn"
                className="p-2 glass rounded-lg hover:bg-secondary/50 transition-all"
              >
                {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4 text-muted-foreground" />}
              </button>
            </div>
            {referralStats && (
              <div className="flex items-center gap-4 mt-3 text-sm text-muted-foreground">
                <span>Приглашено: <strong className="text-foreground">{referralStats.referred_count}</strong></span>
                <span>Заработано: <strong className="text-primary">{referralStats.total_bonus}</strong> б.</span>
              </div>
            )}
            <p className="text-xs text-muted-foreground mt-2">
              Поделитесь кодом — вы получите <strong className="text-primary">50 баллов</strong>, друг получит <strong className="text-primary">25 баллов</strong>
            </p>
          </div>

          {/* Apply referral code */}
          {!user?.referred_by && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">Есть реферальный код?</p>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={referralCode}
                  onChange={e => setReferralCode(e.target.value.toUpperCase())}
                  placeholder="Введите код..."
                  maxLength={8}
                  data-testid="apply-referral-input"
                  className="flex-1 bg-secondary/50 border border-transparent focus:border-primary rounded-lg h-10 px-3 text-foreground placeholder:text-muted-foreground outline-none font-mono uppercase tracking-widest text-center"
                />
                <button
                  onClick={handleApplyReferral}
                  disabled={referralApplying || !referralCode.trim()}
                  data-testid="apply-referral-btn"
                  className="px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 disabled:opacity-50 flex items-center gap-2"
                >
                  {referralApplying ? <Loader2 className="w-4 h-4 animate-spin" /> : <Gift className="w-4 h-4" />}
                  Применить
                </button>
              </div>
              {referralMsg && (
                <p className={`text-sm mt-2 ${referralMsg.includes('Ошибка') || referralMsg.includes('Нельзя') || referralMsg.includes('не найден') || referralMsg.includes('уже') ? 'text-destructive' : 'text-emerald-400'}`}>
                  {referralMsg}
                </p>
              )}
            </div>
          )}
          {user?.referred_by && (
            <p className="text-sm text-emerald-400 flex items-center gap-1">
              <Check className="w-4 h-4" /> Реферальный код уже активирован
            </p>
          )}
        </div>

        {/* Age Group Selection */}
        <div className="glass rounded-xl p-6 mb-6">
          <h3 className="font-semibold text-foreground mb-3">Возрастная группа</h3>
          <div className="grid grid-cols-2 gap-2">
            {ageGroups.map(ag => (
              <button
                key={ag.value}
                onClick={() => handleAgeGroupChange(ag.value)}
                data-testid={`age-group-${ag.value}`}
                className={`p-3 rounded-lg text-sm font-medium transition-all ${
                  user?.age_group === ag.value
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-secondary/50 text-muted-foreground hover:text-foreground hover:bg-secondary'
                }`}
              >
                {ag.label}
              </button>
            ))}
          </div>
        </div>

        {/* Theme Toggle */}
        <div className="glass rounded-xl p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {theme === 'dark' ? <Moon className="w-5 h-5 text-primary" /> : <Sun className="w-5 h-5 text-yellow-500" />}
              <span className="font-medium text-foreground">Тема оформления</span>
            </div>
            <button
              onClick={toggleTheme}
              data-testid="theme-toggle-btn"
              className="px-4 py-2 bg-secondary rounded-lg text-sm font-medium text-foreground hover:bg-secondary/80 transition-colors"
            >
              {theme === 'dark' ? 'Светлая' : 'Тёмная'}
            </button>
          </div>
        </div>

        {/* Text Scale */}
        <div className="glass rounded-xl p-6 mb-6">
          <button
            onClick={() => setShowScaleSettings(!showScaleSettings)}
            className="w-full flex items-center justify-between"
          >
            <div className="flex items-center gap-3">
              <Settings className="w-5 h-5 text-muted-foreground" />
              <span className="font-medium text-foreground">Размер текста</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground font-mono">{textScale}x</span>
              <ChevronRight className={`w-4 h-4 text-muted-foreground transition-transform ${showScaleSettings ? 'rotate-90' : ''}`} />
            </div>
          </button>
          {showScaleSettings && (
            <div className="mt-4 grid grid-cols-3 gap-2">
              {[1, 2, 3, 4, 5, 6].map(s => (
                <button
                  key={s}
                  onClick={() => handleScaleChange(s)}
                  data-testid={`text-scale-${s}`}
                  className={`p-3 rounded-lg text-center font-medium transition-all ${
                    textScale === s
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-secondary/50 text-muted-foreground hover:bg-secondary'
                  }`}
                >
                  {s}x
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Logout */}
        <button
          onClick={handleLogout}
          data-testid="logout-btn"
          className="w-full bg-destructive/10 border border-destructive/20 text-destructive font-medium py-4 rounded-xl hover:bg-destructive/20 transition-all flex items-center justify-center gap-2"
        >
          <LogOut className="w-5 h-5" />
          Выйти из аккаунта
        </button>
      </motion.div>
    </div>
  );
}
