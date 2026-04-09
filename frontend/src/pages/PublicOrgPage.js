import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useParams, Link } from 'react-router-dom';
import { Star, MapPin, FileText, ArrowLeft, CheckCircle2, Clock, Loader2 } from 'lucide-react';
import api from '../lib/api';

function RatingBar({ rating, count, max }) {
  const pct = max > 0 ? (count / max) * 100 : 0;
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-muted-foreground w-3">{rating}</span>
      <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
      <div className="flex-1 bg-secondary/30 rounded-full h-2 overflow-hidden">
        <div className="h-full rounded-full bg-yellow-400 transition-all" style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-muted-foreground w-6 text-right">{count}</span>
    </div>
  );
}

export default function PublicOrgPage() {
  const { orgId } = useParams();
  const [org, setOrg] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/org/${orgId}/public`).then(r => setOrg(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, [orgId]);

  if (loading) return <div className="min-h-screen flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;
  if (!org) return <div className="min-h-screen flex items-center justify-center text-muted-foreground">Организация не найдена</div>;

  const dist = org.rating_distribution || {};
  const maxCount = Math.max(...Object.values(dist), 1);

  return (
    <div className="max-w-3xl mx-auto px-4 py-8" data-testid="public-org-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Link to="/stats" className="flex items-center gap-2 text-sm text-muted-foreground mb-4 hover:text-foreground">
          <ArrowLeft className="w-4 h-4" /> Статистика
        </Link>

        <div className="glass rounded-xl p-6 mb-4">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center shrink-0">
              <FileText className="w-7 h-7 text-primary" />
            </div>
            <div className="flex-1">
              <h1 className="text-xl sm:text-2xl font-bold text-foreground">{org.name}</h1>
              {org.description && <p className="text-sm text-muted-foreground mt-1">{org.description}</p>}
              <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                <MapPin className="w-3.5 h-3.5" /> {org.address}
              </div>
              {org.category && <span className="inline-block mt-2 text-[10px] px-2 py-0.5 rounded-full bg-secondary text-muted-foreground">{org.category}</span>}
            </div>
          </div>

          {/* Rating */}
          <div className="mt-5 flex items-center gap-6">
            <div className="text-center">
              <p className="text-4xl font-bold text-foreground">{org.average_rating?.toFixed(1) || '—'}</p>
              <div className="flex items-center gap-0.5 justify-center mt-1">
                {[1, 2, 3, 4, 5].map(s => (
                  <Star key={s} className={`w-4 h-4 ${s <= Math.round(org.average_rating || 0) ? 'text-yellow-400 fill-yellow-400' : 'text-secondary'}`} />
                ))}
              </div>
              <p className="text-[10px] text-muted-foreground mt-1">{org.review_count} отзывов</p>
            </div>
            <div className="flex-1 space-y-1">
              {[5, 4, 3, 2, 1].map(r => (
                <RatingBar key={r} rating={r} count={dist[r] || dist[String(r)] || 0} max={maxCount} />
              ))}
            </div>
          </div>
        </div>

        {/* Reviews */}
        <h2 className="text-sm font-medium text-muted-foreground mb-3">Отзывы ({org.reviews?.length || 0})</h2>
        {org.reviews?.length === 0 && <p className="text-center text-muted-foreground text-sm py-6 glass rounded-xl">Отзывов пока нет</p>}
        <div className="space-y-2">
          {(org.reviews || []).map(r => (
            <div key={r.review_id} className="glass rounded-xl p-4" data-testid={`review-${r.review_id}`}>
              <div className="flex items-center gap-2 mb-1">
                <div className="flex gap-0.5">
                  {[1, 2, 3, 4, 5].map(s => (
                    <Star key={s} className={`w-3 h-3 ${s <= r.rating ? 'text-yellow-400 fill-yellow-400' : 'text-secondary'}`} />
                  ))}
                </div>
                {r.status === 'approved' && <CheckCircle2 className="w-3 h-3 text-green-400" />}
                {r.status === 'pending' && <Clock className="w-3 h-3 text-yellow-400" />}
                {r.verification_count > 0 && <span className="text-[10px] text-blue-400">{r.verification_count} подтв.</span>}
              </div>
              <h3 className="text-sm font-semibold text-foreground">{r.title}</h3>
              <p className="text-xs text-muted-foreground mt-1 line-clamp-3">{r.content}</p>
              <div className="flex items-center justify-between mt-2">
                <p className="text-[10px] text-muted-foreground">{r.user_name || 'Аноним'}</p>
                <p className="text-[10px] text-muted-foreground">{new Date(r.created_at).toLocaleDateString('ru-RU')}</p>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
