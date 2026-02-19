import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { 
  Star, Clock, CheckCircle2, XCircle, ChevronRight, 
  TrendingUp, Award, Plus, MapPin, ArrowRight
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { reviewsApi } from '../lib/api';

const statusConfig = {
  approved: { label: 'Верифицирован', color: 'text-emerald-400', bg: 'bg-emerald-500/10', glow: 'glow-green', icon: CheckCircle2 },
  pending: { label: 'Ожидает', color: 'text-yellow-400', bg: 'bg-yellow-500/10', glow: 'glow-yellow', icon: Clock },
  rejected: { label: 'Отклонён', color: 'text-red-400', bg: 'bg-red-500/10', glow: 'glow-red', icon: XCircle },
};

function ReviewCard({ review, index }) {
  const config = statusConfig[review.status] || statusConfig.pending;
  const StatusIcon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08 }}
    >
      <Link
        to={`/reviews/${review.review_id}`}
        data-testid={`review-card-${review.review_id}`}
        className="block glass rounded-xl p-5 hover:border-primary/30 transition-all group"
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-foreground truncate group-hover:text-primary transition-colors">
              {review.title}
            </h3>
            <div className="flex items-center gap-1.5 mt-1">
              <MapPin className="w-3.5 h-3.5 text-muted-foreground" />
              <span className="text-sm text-muted-foreground truncate">{review.org_name}</span>
            </div>
          </div>
          <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full ${config.bg} shrink-0 ml-3`}>
            <StatusIcon className={`w-3.5 h-3.5 ${config.color}`} />
            <span className={`text-xs font-medium ${config.color}`}>{config.label}</span>
          </div>
        </div>
        <p className="text-sm text-muted-foreground line-clamp-2 mb-3">{review.content}</p>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1">
            {[1,2,3,4,5].map(s => (
              <Star key={s} className={`w-3.5 h-3.5 ${s <= review.rating ? 'text-yellow-400 fill-yellow-400' : 'text-muted-foreground/30'}`} />
            ))}
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className="font-mono">{review.verification_count}/2</span>
            <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </div>
        </div>
      </Link>
    </motion.div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    reviewsApi.list().then(setReviews).catch(console.error).finally(() => setLoading(false));
  }, []);

  const approvedCount = reviews.filter(r => r.status === 'approved').length;
  const pendingCount = reviews.filter(r => r.status === 'pending').length;

  return (
    <div className="space-y-6" data-testid="dashboard-page">
      {/* Header */}
      <div>
        <motion.h1
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="text-3xl md:text-4xl font-bold tracking-tight"
          style={{ fontFamily: 'Manrope, sans-serif' }}
        >
          Добро пожаловать{user?.name ? `, ${user.name.split(' ')[0]}` : ''}
        </motion.h1>
        <p className="text-muted-foreground mt-1">Обзор активности и отзывов вашего города</p>
      </div>

      {/* Stats Bento Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="glass rounded-xl p-5 group hover:border-primary/30 transition-all"
          data-testid="stat-points"
        >
          <div className="flex items-center gap-2 mb-2">
            <Award className="w-4 h-4 text-primary" />
            <span className="text-xs text-muted-foreground uppercase tracking-wider">Баллы</span>
          </div>
          <p className="text-3xl font-bold text-primary font-mono">{user?.points || 0}</p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
          className="glass rounded-xl p-5"
          data-testid="stat-verified"
        >
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span className="text-xs text-muted-foreground uppercase tracking-wider">Верифицировано</span>
          </div>
          <p className="text-3xl font-bold text-emerald-400 font-mono">{approvedCount}</p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          className="glass rounded-xl p-5"
          data-testid="stat-pending"
        >
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-4 h-4 text-yellow-400" />
            <span className="text-xs text-muted-foreground uppercase tracking-wider">Ожидают</span>
          </div>
          <p className="text-3xl font-bold text-yellow-400 font-mono">{pendingCount}</p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}
          className="glass rounded-xl p-5"
          data-testid="stat-total"
        >
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-blue-400" />
            <span className="text-xs text-muted-foreground uppercase tracking-wider">Всего</span>
          </div>
          <p className="text-3xl font-bold text-foreground font-mono">{reviews.length}</p>
        </motion.div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Link to="/create" data-testid="quick-create-review">
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="bg-primary/10 border border-primary/20 rounded-xl p-6 flex items-center justify-between group cursor-pointer hover:bg-primary/15 transition-all"
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center">
                <Plus className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">Создать отзыв</h3>
                <p className="text-sm text-muted-foreground">Сообщите о проблеме</p>
              </div>
            </div>
            <ArrowRight className="w-5 h-5 text-primary group-hover:translate-x-1 transition-transform" />
          </motion.div>
        </Link>

        <Link to="/map" data-testid="quick-view-map">
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-6 flex items-center justify-between group cursor-pointer hover:bg-emerald-500/15 transition-all"
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                <MapPin className="w-6 h-6 text-emerald-400" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">Карта заведений</h3>
                <p className="text-sm text-muted-foreground">Смотреть на карте</p>
              </div>
            </div>
            <ArrowRight className="w-5 h-5 text-emerald-400 group-hover:translate-x-1 transition-transform" />
          </motion.div>
        </Link>
      </div>

      {/* Reviews Feed */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold tracking-tight">Последние отзывы</h2>
          <Link to="/reviews" className="text-sm text-primary hover:underline flex items-center gap-1">
            Все отзывы <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
        {loading ? (
          <div className="grid gap-3">
            {[1,2,3].map(i => (
              <div key={i} className="glass rounded-xl p-5 animate-pulse">
                <div className="h-4 bg-muted rounded w-3/4 mb-3" />
                <div className="h-3 bg-muted rounded w-1/2 mb-3" />
                <div className="h-3 bg-muted rounded w-full" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid gap-3">
            {reviews.slice(0, 5).map((review, i) => (
              <ReviewCard key={review.review_id} review={review} index={i} />
            ))}
            {reviews.length === 0 && (
              <div className="glass rounded-xl p-8 text-center">
                <p className="text-muted-foreground">Отзывов пока нет. Будьте первым!</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
