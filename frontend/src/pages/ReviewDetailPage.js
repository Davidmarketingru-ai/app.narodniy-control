import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Star, Clock, CheckCircle2, XCircle, MapPin, ArrowLeft, 
  ShieldCheck, Send, Loader2, User, Timer, Camera, Upload, X
} from 'lucide-react';
import { reviewsApi, verificationsApi } from '../lib/api';
import api from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { ShareButton } from '../components/ShareButton';

const statusConfig = {
  approved: { label: 'Верифицирован', color: 'text-emerald-400', bg: 'bg-emerald-500/10', icon: CheckCircle2 },
  pending: { label: 'Ожидает подтверждения', color: 'text-yellow-400', bg: 'bg-yellow-500/10', icon: Clock },
  rejected: { label: 'Отклонён', color: 'text-red-400', bg: 'bg-red-500/10', icon: XCircle },
  expired: { label: 'Истёк (24ч)', color: 'text-gray-400', bg: 'bg-gray-500/10', icon: Timer },
};

export default function ReviewDetailPage() {
  const { reviewId } = useParams();
  const { user } = useAuth();
  const [review, setReview] = useState(null);
  const [verifications, setVerifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [comment, setComment] = useState('');
  const [verifyPhotos, setVerifyPhotos] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [verifyError, setVerifyError] = useState('');

  useEffect(() => {
    Promise.all([
      reviewsApi.get(reviewId),
      verificationsApi.getByReview(reviewId),
    ]).then(([r, v]) => {
      setReview(r);
      setVerifications(v);
    }).catch(console.error).finally(() => setLoading(false));
  }, [reviewId]);

  const handleVerify = async () => {
    setVerifyError('');
    if (verifyPhotos.length === 0) {
      setVerifyError('Прикрепите минимум 1 фото как доказательство посещения');
      return;
    }
    if (!comment.trim() || comment.trim().length < 20) {
      setVerifyError('Напишите комментарий минимум 20 символов о данном заведении');
      return;
    }
    setSubmitting(true);
    try {
      await verificationsApi.create({ review_id: reviewId, comment, photos: verifyPhotos });
      const [r, v] = await Promise.all([
        reviewsApi.get(reviewId),
        verificationsApi.getByReview(reviewId),
      ]);
      setReview(r);
      setVerifications(v);
      setComment('');
      setVerifyPhotos([]);
    } catch (err) {
      setVerifyError(err.response?.data?.detail || 'Ошибка при подтверждении');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!review) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Отзыв не найден</p>
        <Link to="/dashboard" className="text-primary hover:underline mt-2 inline-block">Назад</Link>
      </div>
    );
  }

  const config = statusConfig[review.status] || statusConfig.pending;
  const StatusIcon = config.icon;
  const canVerify = user && review.user_id !== user.user_id && review.status === 'pending';
  const alreadyVerified = verifications.some(v => v.user_id === user?.user_id);

  const timeLeft = review.expires_at ? Math.max(0, new Date(review.expires_at) - new Date()) : 0;
  const hoursLeft = Math.floor(timeLeft / (1000 * 60 * 60));
  const minutesLeft = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));

  return (
    <div className="max-w-2xl mx-auto" data-testid="review-detail-page">
      <Link to="/dashboard" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-4 transition-colors">
        <ArrowLeft className="w-4 h-4" /> Назад
      </Link>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        {/* Status Badge */}
        <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full ${config.bg} mb-4`}>
          <StatusIcon className={`w-4 h-4 ${config.color}`} />
          <span className={`text-sm font-medium ${config.color}`}>{config.label}</span>
        </div>

        {/* Title */}
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight mb-2" style={{ fontFamily: 'Manrope' }}>
          {review.title}
        </h1>

        {/* Org info */}
        <div className="flex items-center gap-2 text-muted-foreground mb-6">
          <MapPin className="w-4 h-4" />
          <span>{review.org_name} — {review.org_address}</span>
        </div>

        {/* Content */}
        <div className="glass rounded-xl p-6 mb-6">
          <p className="text-foreground leading-relaxed">{review.content}</p>
          <div className="flex items-center gap-4 mt-4 pt-4 border-t border-border/50">
            <div className="flex items-center gap-1">
              {[1,2,3,4,5].map(s => (
                <Star key={s} className={`w-4 h-4 ${s <= review.rating ? 'text-yellow-400 fill-yellow-400' : 'text-muted-foreground/30'}`} />
              ))}
            </div>
            <span className="text-sm text-muted-foreground">
              от {review.user_name || 'Аноним'}
            </span>
            <span className="text-xs text-muted-foreground font-mono">
              {new Date(review.created_at).toLocaleDateString('ru-RU')}
            </span>
            <div className="ml-auto">
              <ShareButton
                title={review.title}
                text={`${review.title} — ${review.org_name} | Народный Контроль`}
                url={`${window.location.origin}/reviews/${review.review_id}`}
              />
            </div>
          </div>
        </div>

        {/* Photos */}
        {review.photos?.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-3">Фотографии</h3>
            <div className="flex gap-3 overflow-x-auto">
              {review.photos.map((p, i) => (
                <img key={i} src={p} alt="" className="w-32 h-32 rounded-lg object-cover border border-border/50" />
              ))}
            </div>
          </div>
        )}

        {/* Verification Progress */}
        <div className="glass rounded-xl p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-foreground flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-primary" />
              Подтверждения
            </h3>
            <span className="font-mono text-lg font-bold text-primary">{review.verification_count}/2</span>
          </div>
          <div className="w-full bg-secondary rounded-full h-2 mb-3">
            <div
              className="bg-primary rounded-full h-2 transition-all duration-500"
              style={{ width: `${Math.min(review.verification_count / 2 * 100, 100)}%` }}
            />
          </div>
          {review.status === 'pending' && timeLeft > 0 && (
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <Clock className="w-3 h-3" />
              Осталось: <span className="font-mono">{hoursLeft}ч {minutesLeft}м</span>
            </p>
          )}
        </div>

        {/* Verifications list */}
        {verifications.length > 0 && (
          <div className="space-y-3 mb-6">
            <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Комментарии подтверждений</h3>
            {verifications.map((v, i) => (
              <motion.div
                key={v.verification_id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="glass rounded-lg p-4"
              >
                <div className="flex items-center gap-2 mb-2">
                  <User className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm font-medium text-foreground">{v.user_name || 'Пользователь'}</span>
                  <span className="text-xs text-muted-foreground font-mono">
                    {new Date(v.created_at).toLocaleDateString('ru-RU')}
                  </span>
                </div>
                {v.comment && <p className="text-sm text-muted-foreground">{v.comment}</p>}
              </motion.div>
            ))}
          </div>
        )}

        {/* Verify Form */}
        {canVerify && !alreadyVerified && (
          <div className="glass rounded-xl p-6">
            <h3 className="font-semibold text-foreground mb-1">Подтвердить отзыв</h3>
            <p className="text-xs text-muted-foreground mb-4">Требуется фото-доказательство и описание (мин. 20 символов)</p>
            {verifyError && (
              <p className="text-sm text-destructive mb-3 bg-destructive/10 p-3 rounded-lg">{verifyError}</p>
            )}
            {/* Photo upload */}
            <div className="mb-3">
              <p className="text-xs text-muted-foreground mb-2 font-medium">Фотографии (обязательно)</p>
              <div className="flex gap-2 flex-wrap">
                {verifyPhotos.map((url, i) => (
                  <div key={i} className="relative w-20 h-20 rounded-lg overflow-hidden border border-border/50">
                    <img src={url} alt="" className="w-full h-full object-cover" />
                    <button onClick={() => setVerifyPhotos(prev => prev.filter((_, j) => j !== i))}
                      className="absolute top-0.5 right-0.5 w-5 h-5 bg-black/60 rounded-full flex items-center justify-center">
                      <X className="w-3 h-3 text-white" />
                    </button>
                  </div>
                ))}
                <label className={`w-20 h-20 rounded-lg border-2 border-dashed flex flex-col items-center justify-center cursor-pointer transition-colors ${
                  uploading ? 'border-primary/50 bg-primary/5' : 'border-border/50 hover:border-primary/50'
                }`} data-testid="verify-photo-upload">
                  {uploading ? <Loader2 className="w-5 h-5 animate-spin text-primary" /> : (
                    <>
                      <Camera className="w-5 h-5 text-muted-foreground mb-0.5" />
                      <span className="text-[9px] text-muted-foreground">Фото</span>
                    </>
                  )}
                  <input type="file" accept="image/*" className="hidden" disabled={uploading}
                    onChange={async (e) => {
                      const file = e.target.files?.[0];
                      if (!file) return;
                      setUploading(true);
                      try {
                        const form = new FormData();
                        form.append('file', file);
                        const res = await api.post('/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } });
                        setVerifyPhotos(prev => [...prev, res.data.url]);
                      } catch {}
                      finally { setUploading(false); e.target.value = ''; }
                    }}
                  />
                </label>
              </div>
            </div>
            <textarea
              value={comment}
              onChange={e => setComment(e.target.value)}
              placeholder="Опишите ваш опыт посещения данного заведения (мин. 20 символов)..."
              rows={3}
              data-testid="verify-comment-input"
              className="w-full bg-secondary/50 border border-transparent focus:border-primary rounded-xl p-4 text-foreground placeholder:text-muted-foreground outline-none resize-none mb-1 transition-colors"
            />
            <p className={`text-[10px] mb-3 ${comment.trim().length >= 20 ? 'text-emerald-400' : 'text-muted-foreground'}`}>
              {comment.trim().length}/20 символов
            </p>
            <button
              onClick={handleVerify}
              disabled={submitting || verifyPhotos.length === 0 || comment.trim().length < 20}
              data-testid="verify-review-btn"
              className="bg-emerald-600 text-white font-medium py-3 px-6 rounded-xl hover:bg-emerald-700 transition-all disabled:opacity-50 flex items-center gap-2 shadow-[0_0_15px_rgba(16,185,129,0.3)]"
            >
              {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
              Подтвердить
            </button>
          </div>
        )}
        {alreadyVerified && (
          <div className="glass rounded-xl p-4 text-center">
            <CheckCircle2 className="w-6 h-6 text-emerald-400 mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">Вы уже подтвердили этот отзыв</p>
          </div>
        )}
      </motion.div>
    </div>
  );
}
