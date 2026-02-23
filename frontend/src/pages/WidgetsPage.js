import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  Cloud, Sun, CloudRain, CloudSnow, CloudLightning, CloudDrizzle, Wind,
  DollarSign, TrendingUp, TrendingDown, Minus, Zap, Search, MapPin,
  Thermometer, Droplets, Eye, ArrowUp, ArrowDown, Loader2, AlertTriangle
} from 'lucide-react';
import { widgetsApi } from '../lib/api';

const weatherCodes = {
  0: { icon: Sun, label: 'Ясно' }, 1: { icon: Sun, label: 'Преим. ясно' },
  2: { icon: Cloud, label: 'Облачно' }, 3: { icon: Cloud, label: 'Пасмурно' },
  45: { icon: Cloud, label: 'Туман' }, 48: { icon: Cloud, label: 'Туман' },
  51: { icon: CloudDrizzle, label: 'Морось' }, 53: { icon: CloudDrizzle, label: 'Морось' },
  61: { icon: CloudRain, label: 'Дождь' }, 63: { icon: CloudRain, label: 'Дождь' },
  65: { icon: CloudRain, label: 'Сильный дождь' }, 71: { icon: CloudSnow, label: 'Снег' },
  73: { icon: CloudSnow, label: 'Снег' }, 75: { icon: CloudSnow, label: 'Сильный снег' },
  80: { icon: CloudRain, label: 'Ливень' }, 95: { icon: CloudLightning, label: 'Гроза' },
};

const uvLevels = [
  { max: 2, label: 'Низкий', color: '#10b981' }, { max: 5, label: 'Умеренный', color: '#eab308' },
  { max: 7, label: 'Высокий', color: '#f97316' }, { max: 10, label: 'Очень высокий', color: '#ef4444' },
  { max: 99, label: 'Экстремальный', color: '#7c3aed' },
];

const kpLevels = [
  { max: 3, label: 'Спокойно', color: '#10b981' }, { max: 4, label: 'Небольшие', color: '#eab308' },
  { max: 6, label: 'Буря', color: '#f97316' }, { max: 9, label: 'Сильная буря', color: '#ef4444' },
];

function getUvLevel(uv) { return uvLevels.find(l => uv <= l.max) || uvLevels[4]; }
function getKpLevel(kp) { return kpLevels.find(l => kp <= l.max) || kpLevels[3]; }

export default function WidgetsPage() {
  const [weather, setWeather] = useState(null);
  const [currency, setCurrency] = useState(null);
  const [magnetic, setMagnetic] = useState(null);
  const [locationQuery, setLocationQuery] = useState('');
  const [locations, setLocations] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState({ name: 'Владикавказ', latitude: 43.023, longitude: 44.682 });
  const [showLocations, setShowLocations] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async (lat, lon) => {
    setLoading(true);
    try {
      const [w, c, m] = await Promise.all([
        widgetsApi.weather(lat, lon).catch(() => null),
        widgetsApi.currency().catch(() => null),
        widgetsApi.magnetic().catch(() => null),
      ]);
      setWeather(w); setCurrency(c); setMagnetic(m);
    } catch {} finally { setLoading(false); }
  }, []);

  useEffect(() => {
    fetchData(selectedLocation.latitude, selectedLocation.longitude);
  }, [selectedLocation, fetchData]);

  const handleLocationSearch = async (q) => {
    setLocationQuery(q);
    if (q.length >= 2) {
      const res = await widgetsApi.searchLocations(q);
      setLocations(res); setShowLocations(true);
    } else { setLocations([]); setShowLocations(false); }
  };

  const selectLocation = (loc) => {
    setSelectedLocation(loc); setLocationQuery(''); setShowLocations(false);
  };

  const currentWeather = weather?.current;
  const wCode = currentWeather?.weather_code ?? 0;
  const wInfo = weatherCodes[wCode] || weatherCodes[0];
  const WIcon = wInfo.icon;
  const uvIndex = currentWeather?.uv_index ?? 0;
  const uvLevel = getUvLevel(uvIndex);

  const latestKp = magnetic?.data?.length > 0 ? magnetic.data[magnetic.data.length - 1] : null;
  const kpLevel = latestKp ? getKpLevel(latestKp.kp) : null;

  const dailyDays = ['Сегодня', 'Завтра', 'Послезавтра'];

  return (
    <div data-testid="widgets-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold tracking-tight mb-2" style={{ fontFamily: 'Manrope' }}>Информация</h1>

        {/* Location Selector */}
        <div className="relative mb-6">
          <div className="flex items-center gap-2 glass rounded-xl p-3">
            <MapPin className="w-4 h-4 text-primary shrink-0" />
            <span className="text-sm text-foreground font-medium">{selectedLocation.name}</span>
            <span className="text-xs text-muted-foreground">{selectedLocation.admin1 || ''}</span>
            <div className="ml-auto relative flex-1 max-w-[200px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3 h-3 text-muted-foreground" />
              <input type="text" value={locationQuery} onChange={e => handleLocationSearch(e.target.value)} placeholder="Сменить..." data-testid="location-search-input"
                className="w-full bg-secondary/50 rounded-lg h-8 pl-8 pr-3 text-xs text-foreground placeholder:text-muted-foreground outline-none" />
            </div>
          </div>
          {showLocations && locations.length > 0 && (
            <div className="absolute right-0 top-full mt-1 glass rounded-xl overflow-hidden z-50 w-72 max-h-48 overflow-y-auto">
              {locations.map((loc, i) => (
                <button key={i} onClick={() => selectLocation(loc)} className="w-full p-3 text-left hover:bg-primary/10 transition-colors flex items-center gap-2">
                  <MapPin className="w-3 h-3 text-muted-foreground shrink-0" />
                  <div><p className="text-sm text-foreground">{loc.name}</p><p className="text-[10px] text-muted-foreground">{loc.admin1}, {loc.country}</p></div>
                </button>
              ))}
            </div>
          )}
        </div>

        {loading ? (
          <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Weather */}
            {weather && (
              <div className="glass rounded-xl p-6 md:col-span-2" data-testid="weather-widget">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Погода</p>
                    <div className="flex items-end gap-3">
                      <p className="text-5xl font-bold text-foreground font-mono">{Math.round(currentWeather?.temperature_2m ?? 0)}<span className="text-2xl text-muted-foreground">°C</span></p>
                      <div>
                        <p className="text-sm text-foreground">{wInfo.label}</p>
                        <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
                          <span className="flex items-center gap-1"><Droplets className="w-3 h-3" />{currentWeather?.relative_humidity_2m ?? 0}%</span>
                          <span className="flex items-center gap-1"><Wind className="w-3 h-3" />{Math.round(currentWeather?.wind_speed_10m ?? 0)} км/ч</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <WIcon className="w-16 h-16 text-primary opacity-60" />
                </div>
                {/* 3-day forecast */}
                <div className="grid grid-cols-3 gap-3">
                  {weather.daily?.temperature_2m_max?.slice(0, 3).map((max, i) => {
                    const min = weather.daily.temperature_2m_min[i];
                    const code = weather.daily.weather_code[i];
                    const info = weatherCodes[code] || weatherCodes[0];
                    const DIcon = info.icon;
                    return (
                      <div key={i} className="bg-secondary/30 rounded-lg p-3 text-center">
                        <p className="text-xs text-muted-foreground mb-1">{dailyDays[i]}</p>
                        <DIcon className="w-6 h-6 mx-auto mb-1 text-muted-foreground" />
                        <p className="text-sm font-mono"><span className="text-foreground">{Math.round(max)}°</span> <span className="text-muted-foreground">{Math.round(min)}°</span></p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* UV Index */}
            <div className="glass rounded-xl p-6" data-testid="uv-widget">
              <p className="text-xs text-muted-foreground uppercase tracking-wider mb-3">УФ-излучение</p>
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-2xl flex items-center justify-center" style={{ backgroundColor: uvLevel.color + '20' }}>
                  <Sun className="w-8 h-8" style={{ color: uvLevel.color }} />
                </div>
                <div>
                  <p className="text-3xl font-bold font-mono" style={{ color: uvLevel.color }}>{Math.round(uvIndex * 10) / 10}</p>
                  <p className="text-sm" style={{ color: uvLevel.color }}>{uvLevel.label}</p>
                </div>
              </div>
              <div className="w-full bg-secondary rounded-full h-2 mt-4">
                <div className="rounded-full h-2 transition-all" style={{ width: `${Math.min(uvIndex / 11 * 100, 100)}%`, backgroundColor: uvLevel.color }} />
              </div>
            </div>

            {/* Magnetic Storms */}
            <div className="glass rounded-xl p-6" data-testid="magnetic-widget">
              <p className="text-xs text-muted-foreground uppercase tracking-wider mb-3">Магнитные бури</p>
              {latestKp ? (
                <>
                  <div className="flex items-center gap-4 mb-3">
                    <div className="w-16 h-16 rounded-2xl flex items-center justify-center" style={{ backgroundColor: kpLevel.color + '20' }}>
                      <Zap className="w-8 h-8" style={{ color: kpLevel.color }} />
                    </div>
                    <div>
                      <p className="text-3xl font-bold font-mono" style={{ color: kpLevel.color }}>Kp {latestKp.kp}</p>
                      <p className="text-sm" style={{ color: kpLevel.color }}>{kpLevel.label}</p>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    {(magnetic?.data || []).map((d, i) => {
                      const lvl = getKpLevel(d.kp);
                      return <div key={i} className="flex-1 rounded" style={{ height: `${Math.max(d.kp * 6, 4)}px`, backgroundColor: lvl.color, opacity: 0.7 }} title={`Kp ${d.kp}`} />;
                    })}
                  </div>
                </>
              ) : <p className="text-muted-foreground text-sm">Данные загружаются...</p>}
            </div>

            {/* Currency Rates */}
            {currency && (
              <div className="glass rounded-xl p-6 md:col-span-2" data-testid="currency-widget">
                <p className="text-xs text-muted-foreground uppercase tracking-wider mb-3">Курсы валют ЦБ РФ</p>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  {Object.entries(currency.rates || {}).map(([code, r]) => {
                    const diff = r.value - r.previous;
                    const isUp = diff > 0;
                    const isDown = diff < 0;
                    return (
                      <div key={code} className="bg-secondary/30 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-bold text-foreground">{code}</span>
                          {isUp ? <ArrowUp className="w-3 h-3 text-red-400" /> : isDown ? <ArrowDown className="w-3 h-3 text-emerald-400" /> : <Minus className="w-3 h-3 text-muted-foreground" />}
                        </div>
                        <p className="text-lg font-bold font-mono text-foreground">{(r.value / r.nominal).toFixed(2)}</p>
                        <p className={`text-xs font-mono ${isUp ? 'text-red-400' : isDown ? 'text-emerald-400' : 'text-muted-foreground'}`}>
                          {isUp ? '+' : ''}{(diff / r.nominal).toFixed(4)}
                        </p>
                        <p className="text-[10px] text-muted-foreground mt-0.5">{r.name}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </motion.div>
    </div>
  );
}
