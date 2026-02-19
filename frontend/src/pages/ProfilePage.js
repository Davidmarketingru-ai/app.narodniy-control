import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  User, Shield, Award, Settings, LogOut, Sun, Moon, ChevronRight
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { profileApi } from '../lib/api';
import { useNavigate } from 'react-router-dom';

export default function ProfilePage() {
  const { user, logout, refreshUser } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [textScale, setTextScale] = useState(user?.text_scale || 1);
  const [showScaleSettings, setShowScaleSettings] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleScaleChange = async (newScale) => {
    setTextScale(newScale);
    try {
      await profileApi.update({ text_scale: newScale });
      await refreshUser();
    } catch {}
  };

  const handleAgeGroupChange = async (ageGroup) => {
    try {
      await profileApi.update({ age_group: ageGroup });
      await refreshUser();
    } catch {}
  };

  const ageGroups = [
    { value: '18-25', label: '18-25 лет' },
    { value: '26-40', label: '26-40 лет' },
    { value: '41-60', label: '41-60 лет' },
    { value: '60+', label: '60+ лет' },
  ];

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
            </div>
          </div>
          <div className="flex items-center gap-2 pt-4 border-t border-border/50">
            {user?.is_verified ? (
              <div className="flex items-center gap-2 text-emerald-400">
                <Shield className="w-4 h-4" />
                <span className="text-sm font-medium">Верифицирован</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-yellow-400">
                <Shield className="w-4 h-4" />
                <span className="text-sm font-medium">Не верифицирован</span>
              </div>
            )}
          </div>
        </div>

        {/* Points */}
        <div className="bg-gradient-to-r from-primary/20 to-primary/5 border border-primary/20 rounded-xl p-6 mb-6" data-testid="profile-points">
          <div className="flex items-center gap-2 mb-2">
            <Award className="w-5 h-5 text-primary" />
            <span className="text-sm text-muted-foreground uppercase tracking-wider">Ваши баллы</span>
          </div>
          <p className="text-4xl font-bold text-primary font-mono">{user?.points || 0}</p>
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
