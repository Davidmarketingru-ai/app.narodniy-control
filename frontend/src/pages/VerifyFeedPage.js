import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  ShieldCheck, Clock, MapPin, Star, ChevronRight, Loader2, Search, AlertCircle
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { verifyFeedApi } from '../lib/api';

export default function VerifyFeedPage() {
  const { user } = useAuth();
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    verifyFeedApi.pending().then(setReviews).catch(console.error).finally(() => setLoading(false));
  }, []);

  const getTimeLeft = (expiresAt) => {
    const diff = new Date(expiresAt) - new Date();
    if (diff <= 0) return { text: 'Истекло', urgent: true };
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    if (hours < 6) return { text: `${hours}ч ${mins}м`, urgent: true };
    return { text: `${hours}ч ${mins}м`, urgent: false };
  };

  return (
    <div className="max-w-3xl mx-auto" data-testid="verify-feed-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight" style={{ fontFamily: 'Manrope' }}>
            Помогите проверить
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            Подтвердите отзывы других пользователей и получите 5 баллов за каждый
          </p>
        </div>

        {/* Info banner */}
        <div className="bg-primary/10 border border-primary/20 rounded-xl p-4 mb-6 flex items-start gap-3" data-testid="verify-info-banner">
          <ShieldCheck className="w-5 h-5 text-primary shrink-0 mt-0.5" />
          <div>
            <p className="text-sm text-foreground font-medium">Как это работает?</p>
            <p className="text-xs text-muted-foreground mt-1">
              Каждый отзыв нуждается в 2 подтверждениях. Перейдите на страницу отзыва, 
              изучите информацию и нажмите «Подтвердить», если она верна. 
              Вы получите <strong className="text-primary">5 баллов</strong> за каждое подтверждение.
            </p>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : reviews.length === 0 ? (
          <div className="glass rounded-xl p-10 text-center" data-testid="verify-empty-state">
            <ShieldCheck className="w-14 h-14 text-muted-foreground/20 mx-auto mb-4" />
            <p className="text-lg font-medium text-foreground mb-1">Всё проверено!</p>
            <p className="text-sm text-muted-foreground">
              Сейчас нет отзывов, ожидающих вашего подтверждения. Загляните позже.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-xs text-muted-foreground uppercase tracking-wider mb-2">
              {reviews.length} отзывов ожидают проверки
            </p>
            {reviews.map((review, i) => {
              const timeInfo = getTimeLeft(review.expires_at);
              return (
                <motion.div
                  key={review.review_id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <Link
                    to={`/reviews/${review.review_id}`}
                    data-testid={`verify-card-${review.review_id}`}
                    className="block glass rounded-xl p-5 hover:border-primary/30 transition-all group"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-foreground truncate group-hover:text-primary transition-colors">
                          {review.title}
                        </h3>
                        <div className="flex items-center gap-1.5 mt-1">
                          <MapPin className="w-3.5 h-3.5 text-muted-foreground" />
                          <span className="text-sm text-muted-foreground truncate">{review.org_name}</span>
                        </div>
                      </div>
                      <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full shrink-0 ml-3 ${
                        timeInfo.urgent ? 'bg-red-500/10' : 'bg-yellow-500/10'
                      }`}>
                        <Clock className={`w-3.5 h-3.5 ${timeInfo.urgent ? 'text-red-400' : 'text-yellow-400'}`} />
                        <span className={`text-xs font-mono font-medium ${timeInfo.urgent ? 'text-red-400' : 'text-yellow-400'}`}>
                          {timeInfo.text}
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2 mb-3">{review.content}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="flex items-center gap-1">
                          {[1,2,3,4,5].map(s => (
                            <Star key={s} className={`w-3 h-3 ${s <= review.rating ? 'text-yellow-400 fill-yellow-400' : 'text-muted-foreground/20'}`} />
                          ))}
                        </div>
                        <span className="text-xs font-mono text-muted-foreground">{review.verification_count}/2 подтв.</span>
                      </div>
                      <div className="flex items-center gap-1 text-xs text-primary font-medium">
                        Проверить <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                      </div>
                    </div>
                  </Link>
                </motion.div>
              );
            })}
          </div>
        )}
      </motion.div>
    </div>
  );
}
