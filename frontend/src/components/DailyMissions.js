import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  ShieldCheck, Newspaper, MapPin, Flame, Gift, Check, Loader2, ChevronRight
} from 'lucide-react';
import { missionsApi } from '../lib/api';

const ICON_MAP = {
  'shield-check': ShieldCheck,
  'newspaper': Newspaper,
  'map-pin': MapPin,
};

export function DailyMissions() {
  const [data, setData] = useState(null);
  const [claiming, setClaiming] = useState(null);

  useEffect(() => {
    missionsApi.daily().then(setData).catch(() => {});
  }, []);

  const handleClaim = async (missionId) => {
    setClaiming(missionId);
    try {
      await missionsApi.claim(missionId);
      const fresh = await missionsApi.daily();
      setData(fresh);
    } catch {}
    finally { setClaiming(null); }
  };

  if (!data) return null;

  const { missions, streak } = data;
  const allDone = missions.every(m => m.claimed);

  return (
    <div className="glass rounded-xl p-5" data-testid="daily-missions">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-foreground flex items-center gap-2">
          <Gift className="w-5 h-5 text-primary" />
          Ежедневные миссии
        </h3>
        {streak > 0 && (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-orange-500/10" data-testid="streak-badge">
            <Flame className="w-3.5 h-3.5 text-orange-400" />
            <span className="text-xs font-bold text-orange-400 font-mono">{streak}</span>
            <span className="text-[10px] text-orange-400/70">дн.</span>
          </div>
        )}
      </div>

      <div className="space-y-2">
        {missions.map((m) => {
          const Icon = ICON_MAP[m.icon] || Gift;
          const completed = m.progress >= m.target;
          const pct = Math.min((m.progress / m.target) * 100, 100);
          return (
            <div key={m.mission_id} className={`flex items-center gap-3 p-3 rounded-lg transition-all ${
              m.claimed ? 'bg-emerald-500/5 opacity-60' : 'bg-secondary/30'
            }`} data-testid={`mission-${m.type}`}>
              <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${
                m.claimed ? 'bg-emerald-500/20' : 'bg-primary/10'
              }`}>
                {m.claimed ? <Check className="w-4 h-4 text-emerald-400" /> : <Icon className="w-4 h-4 text-primary" />}
              </div>
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium ${m.claimed ? 'text-muted-foreground line-through' : 'text-foreground'}`}>
                  {m.title}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  <div className="flex-1 bg-secondary rounded-full h-1.5 max-w-[120px]">
                    <div className="rounded-full h-1.5 transition-all" style={{
                      width: `${pct}%`,
                      backgroundColor: m.claimed ? '#10b981' : '#3b82f6'
                    }} />
                  </div>
                  <span className="text-[10px] text-muted-foreground font-mono">{m.progress}/{m.target}</span>
                </div>
              </div>
              <div className="shrink-0">
                {m.claimed ? (
                  <span className="text-[10px] text-emerald-400 font-medium">Готово</span>
                ) : completed ? (
                  <button onClick={() => handleClaim(m.mission_id)} disabled={claiming === m.mission_id}
                    data-testid={`claim-${m.type}`}
                    className="px-3 py-1.5 bg-primary text-primary-foreground text-xs font-medium rounded-lg hover:bg-primary/90 transition-all disabled:opacity-50">
                    {claiming === m.mission_id ? <Loader2 className="w-3 h-3 animate-spin" /> : `+${m.reward}`}
                  </button>
                ) : (
                  <span className="text-[10px] text-muted-foreground font-mono">+{m.reward}</span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {streak >= 7 && (
        <div className="mt-3 text-center text-xs text-orange-400 flex items-center justify-center gap-1">
          <Flame className="w-3 h-3" /> Серия {streak} дней — x1.5 к наградам!
        </div>
      )}
    </div>
  );
}
