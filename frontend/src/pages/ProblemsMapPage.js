import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { motion } from 'framer-motion';
import { MapPin, AlertTriangle, CheckCircle2, Clock, Timer, Star, Filter } from 'lucide-react';
import { mapApi } from '../lib/api';
import { Link } from 'react-router-dom';

const statusConfig = {
  approved: { label: 'Решено', color: '#10b981', radius: 8 },
  pending: { label: 'Ожидает', color: '#eab308', radius: 10 },
  rejected: { label: 'Отклонено', color: '#ef4444', radius: 6 },
  expired: { label: 'Истекло', color: '#6b7280', radius: 5 },
};

export default function ProblemsMapPage() {
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('');

  useEffect(() => {
    mapApi.problems().then(setProblems).catch(console.error).finally(() => setLoading(false));
  }, []);

  const filtered = filterStatus ? problems.filter(p => p.status === filterStatus) : problems;

  const statusCounts = {
    pending: problems.filter(p => p.status === 'pending').length,
    approved: problems.filter(p => p.status === 'approved').length,
    rejected: problems.filter(p => p.status === 'rejected').length,
    expired: problems.filter(p => p.status === 'expired').length,
  };

  return (
    <div className="h-[calc(100vh-80px)] md:h-[calc(100vh-32px)] flex flex-col" data-testid="problems-map-page">
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-3">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h1 className="text-2xl font-bold tracking-tight" style={{ fontFamily: 'Manrope' }}>Карта проблем</h1>
            <p className="text-xs text-muted-foreground">{filtered.length} из {problems.length} проблем</p>
          </div>
        </div>

        {/* Status filters with counts */}
        <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
          <button onClick={() => setFilterStatus('')}
            className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all flex items-center gap-1.5 ${!filterStatus ? 'bg-primary text-primary-foreground' : 'glass text-muted-foreground'}`}>
            Все <span className="font-mono">{problems.length}</span>
          </button>
          {Object.entries(statusConfig).map(([key, cfg]) => (
            <button key={key} onClick={() => setFilterStatus(filterStatus === key ? '' : key)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all flex items-center gap-1.5 ${filterStatus === key ? 'text-white' : 'glass text-muted-foreground'}`}
              style={filterStatus === key ? { backgroundColor: cfg.color } : {}}>
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: cfg.color }} />
              {cfg.label} <span className="font-mono">{statusCounts[key]}</span>
            </button>
          ))}
        </div>
      </motion.div>

      {/* Map */}
      <div className="flex-1 rounded-xl overflow-hidden border border-border/50 relative">
        <MapContainer center={[43.023, 44.682]} zoom={13} className="w-full h-full" zoomControl={false}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; OpenStreetMap' />
          {filtered.map(p => {
            const cfg = statusConfig[p.status] || statusConfig.pending;
            return (
              <CircleMarker
                key={p.review_id}
                center={[p.latitude, p.longitude]}
                radius={cfg.radius}
                pathOptions={{
                  fillColor: cfg.color, fillOpacity: 0.7,
                  color: cfg.color, weight: 2, opacity: 0.9,
                }}
              >
                <Popup>
                  <div className="p-1 min-w-[180px]">
                    <h3 className="font-semibold text-sm mb-1">{p.title}</h3>
                    <p className="text-xs text-gray-600 mb-1">{p.org_name}</p>
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: cfg.color }} />
                      <span className="text-xs" style={{ color: cfg.color }}>{cfg.label}</span>
                      <span className="text-xs text-gray-500">{p.verification_count}/2</span>
                    </div>
                    <div className="flex items-center gap-1">
                      {[1,2,3,4,5].map(s => (
                        <Star key={s} className={`w-3 h-3 ${s <= p.rating ? 'text-yellow-500 fill-yellow-500' : 'text-gray-300'}`} />
                      ))}
                    </div>
                    <Link to={`/reviews/${p.review_id}`} className="text-xs text-blue-500 hover:underline mt-1 block">Подробнее</Link>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}
        </MapContainer>

        {/* Legend */}
        <div className="absolute bottom-4 left-4 glass rounded-lg p-3 z-[1000]">
          <p className="text-xs font-medium text-foreground mb-2">Легенда</p>
          <div className="space-y-1">
            {Object.entries(statusConfig).map(([key, cfg]) => (
              <div key={key} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: cfg.color }} />
                <span className="text-[10px] text-muted-foreground">{cfg.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Problems list below map */}
      <div className="mt-3 space-y-2 max-h-36 overflow-y-auto">
        {filtered.slice(0, 5).map(p => {
          const cfg = statusConfig[p.status] || statusConfig.pending;
          return (
            <Link key={p.review_id} to={`/reviews/${p.review_id}`} className="glass rounded-lg p-3 flex items-center justify-between block" data-testid={`problem-${p.review_id}`}>
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: cfg.color }} />
                <div>
                  <p className="text-sm font-medium text-foreground truncate">{p.title}</p>
                  <p className="text-xs text-muted-foreground">{p.org_name}</p>
                </div>
              </div>
              <span className="text-xs font-mono text-muted-foreground">{p.verification_count}/2</span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
