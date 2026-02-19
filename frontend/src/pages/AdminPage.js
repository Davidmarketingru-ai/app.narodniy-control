import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Shield, Users, FileText, CheckCircle2, XCircle, Clock,
  BarChart3, Loader2, ChevronDown, Timer, Eye
} from 'lucide-react';
import { adminApi } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router-dom';

const statusConfig = {
  approved: { label: 'Одобрен', color: 'text-emerald-400', bg: 'bg-emerald-500/10', icon: CheckCircle2 },
  pending: { label: 'Ожидает', color: 'text-yellow-400', bg: 'bg-yellow-500/10', icon: Clock },
  rejected: { label: 'Отклонён', color: 'text-red-400', bg: 'bg-red-500/10', icon: XCircle },
  expired: { label: 'Истёк', color: 'text-gray-400', bg: 'bg-gray-500/10', icon: Timer },
};

export default function AdminPage() {
  const { user } = useAuth();
  const [tab, setTab] = useState('reviews');
  const [stats, setStats] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [users, setUsers] = useState([]);
  const [filterStatus, setFilterStatus] = useState('pending');
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectModal, setShowRejectModal] = useState(null);

  useEffect(() => {
    if (user?.role !== 'admin') return;
    setLoading(true);
    if (tab === 'reviews') {
      adminApi.reviews(filterStatus).then(setReviews).catch(console.error).finally(() => setLoading(false));
    } else if (tab === 'users') {
      adminApi.users().then(setUsers).catch(console.error).finally(() => setLoading(false));
    } else if (tab === 'stats') {
      adminApi.stats().then(setStats).catch(console.error).finally(() => setLoading(false));
    }
  }, [tab, filterStatus, user]);

  const handleApprove = async (reviewId) => {
    setActionLoading(reviewId);
    try {
      await adminApi.approveReview(reviewId);
      setReviews(prev => prev.filter(r => r.review_id !== reviewId));
    } catch (err) { console.error(err); }
    finally { setActionLoading(null); }
  };

  const handleReject = async () => {
    if (!showRejectModal) return;
    setActionLoading(showRejectModal);
    try {
      await adminApi.rejectReview(showRejectModal, rejectReason);
      setReviews(prev => prev.filter(r => r.review_id !== showRejectModal));
    } catch (err) { console.error(err); }
    finally { setActionLoading(null); setShowRejectModal(null); setRejectReason(''); }
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      await adminApi.setRole(userId, newRole);
      setUsers(prev => prev.map(u => u.user_id === userId ? { ...u, role: newRole } : u));
    } catch (err) { console.error(err); }
  };

  if (user?.role !== 'admin') {
    return (
      <div className="text-center py-12" data-testid="admin-no-access">
        <Shield className="w-16 h-16 text-muted-foreground/30 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-foreground mb-2">Доступ запрещён</h2>
        <p className="text-muted-foreground">У вас нет прав администратора</p>
      </div>
    );
  }

  return (
    <div data-testid="admin-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3 mb-6">
          <Shield className="w-6 h-6 text-primary" />
          <h1 className="text-3xl font-bold tracking-tight" style={{ fontFamily: 'Manrope' }}>
            Админ-панель
          </h1>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto">
          {[
            { id: 'reviews', label: 'Отзывы', icon: FileText },
            { id: 'users', label: 'Пользователи', icon: Users },
            { id: 'stats', label: 'Статистика', icon: BarChart3 },
          ].map(t => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              data-testid={`admin-tab-${t.id}`}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all whitespace-nowrap ${
                tab === t.id ? 'bg-primary text-primary-foreground' : 'glass text-muted-foreground hover:text-foreground'
              }`}
            >
              <t.icon className="w-4 h-4" />
              {t.label}
            </button>
          ))}
        </div>

        {/* Reviews Tab */}
        {tab === 'reviews' && (
          <>
            <div className="flex gap-2 mb-4 flex-wrap">
              {['pending', 'approved', 'rejected', 'expired'].map(s => (
                <button
                  key={s}
                  onClick={() => setFilterStatus(s)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                    filterStatus === s
                      ? `${statusConfig[s].bg} ${statusConfig[s].color} border border-current/20`
                      : 'glass text-muted-foreground hover:text-foreground'
                  }`}
                >
                  {statusConfig[s].label}
                </button>
              ))}
            </div>
            {loading ? (
              <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-primary" /></div>
            ) : reviews.length === 0 ? (
              <div className="glass rounded-xl p-8 text-center">
                <p className="text-muted-foreground">Нет отзывов с таким статусом</p>
              </div>
            ) : (
              <div className="space-y-3">
                {reviews.map((review, i) => {
                  const sc = statusConfig[review.status] || statusConfig.pending;
                  const SC = sc.icon;
                  return (
                    <motion.div
                      key={review.review_id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.05 }}
                      className="glass rounded-xl p-5"
                      data-testid={`admin-review-${review.review_id}`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-foreground">{review.title}</h3>
                          <p className="text-sm text-muted-foreground mt-1">{review.org_name} — {review.org_address}</p>
                        </div>
                        <div className={`flex items-center gap-1 px-2 py-1 rounded-full ${sc.bg}`}>
                          <SC className={`w-3 h-3 ${sc.color}`} />
                          <span className={`text-xs ${sc.color}`}>{sc.label}</span>
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2 mb-3">{review.content}</p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3 text-xs text-muted-foreground">
                          <span>от: {review.user_name || 'Аноним'}</span>
                          <span className="font-mono">{review.verification_count}/2 подтв.</span>
                          <span className="font-mono">{new Date(review.created_at).toLocaleDateString('ru-RU')}</span>
                        </div>
                        <div className="flex gap-2">
                          <Link to={`/reviews/${review.review_id}`} className="p-2 glass rounded-lg hover:bg-secondary/50">
                            <Eye className="w-4 h-4 text-muted-foreground" />
                          </Link>
                          {review.status === 'pending' && (
                            <>
                              <button
                                onClick={() => handleApprove(review.review_id)}
                                disabled={actionLoading === review.review_id}
                                data-testid={`admin-approve-${review.review_id}`}
                                className="px-3 py-1.5 bg-emerald-600 text-white text-xs font-medium rounded-lg hover:bg-emerald-700 transition-all disabled:opacity-50"
                              >
                                {actionLoading === review.review_id ? <Loader2 className="w-3 h-3 animate-spin" /> : 'Одобрить'}
                              </button>
                              <button
                                onClick={() => setShowRejectModal(review.review_id)}
                                data-testid={`admin-reject-${review.review_id}`}
                                className="px-3 py-1.5 bg-destructive/10 text-destructive text-xs font-medium rounded-lg hover:bg-destructive/20 transition-all"
                              >
                                Отклонить
                              </button>
                            </>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            )}
          </>
        )}

        {/* Users Tab */}
        {tab === 'users' && (
          loading ? (
            <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-primary" /></div>
          ) : (
            <div className="space-y-2">
              {users.map((u, i) => (
                <motion.div
                  key={u.user_id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.03 }}
                  className="glass rounded-xl p-4 flex items-center justify-between"
                  data-testid={`admin-user-${u.user_id}`}
                >
                  <div className="flex items-center gap-3">
                    {u.picture ? (
                      <img src={u.picture} alt="" className="w-9 h-9 rounded-full object-cover" />
                    ) : (
                      <div className="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center">
                        <Users className="w-4 h-4 text-primary" />
                      </div>
                    )}
                    <div>
                      <p className="text-sm font-medium text-foreground">{u.name || 'Без имени'}</p>
                      <p className="text-xs text-muted-foreground">{u.email} — {u.points || 0} баллов</p>
                    </div>
                  </div>
                  <select
                    value={u.role || 'user'}
                    onChange={e => handleRoleChange(u.user_id, e.target.value)}
                    className="bg-secondary text-foreground text-xs px-3 py-1.5 rounded-lg border border-border/50 outline-none"
                  >
                    <option value="user">Пользователь</option>
                    <option value="admin">Администратор</option>
                  </select>
                </motion.div>
              ))}
            </div>
          )
        )}

        {/* Stats Tab */}
        {tab === 'stats' && (
          loading || !stats ? (
            <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-primary" /></div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Пользователи', value: stats.total_users, color: 'text-primary' },
                { label: 'Отзывы', value: stats.total_reviews, color: 'text-foreground' },
                { label: 'Ожидают', value: stats.pending_reviews, color: 'text-yellow-400' },
                { label: 'Одобрено', value: stats.approved_reviews, color: 'text-emerald-400' },
                { label: 'Отклонено', value: stats.rejected_reviews, color: 'text-red-400' },
                { label: 'Истекло', value: stats.expired_reviews, color: 'text-gray-400' },
                { label: 'Заведения', value: stats.total_organizations, color: 'text-blue-400' },
                { label: 'Подтверждения', value: stats.total_verifications, color: 'text-purple-400' },
              ].map((s, i) => (
                <motion.div
                  key={s.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="glass rounded-xl p-5"
                  data-testid={`admin-stat-${s.label}`}
                >
                  <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">{s.label}</p>
                  <p className={`text-3xl font-bold font-mono ${s.color}`}>{s.value}</p>
                </motion.div>
              ))}
            </div>
          )
        )}

        {/* Reject Modal */}
        {showRejectModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowRejectModal(null)}>
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              onClick={e => e.stopPropagation()}
              className="glass rounded-xl p-6 w-full max-w-md"
            >
              <h3 className="font-semibold text-foreground mb-3">Причина отклонения</h3>
              <textarea
                value={rejectReason}
                onChange={e => setRejectReason(e.target.value)}
                placeholder="Укажите причину..."
                rows={3}
                data-testid="reject-reason-input"
                className="w-full bg-secondary/50 border border-transparent focus:border-destructive rounded-xl p-3 text-foreground placeholder:text-muted-foreground outline-none resize-none mb-4"
              />
              <div className="flex gap-2 justify-end">
                <button onClick={() => setShowRejectModal(null)} className="px-4 py-2 glass rounded-lg text-sm text-muted-foreground hover:text-foreground">
                  Отмена
                </button>
                <button onClick={handleReject} data-testid="confirm-reject-btn" className="px-4 py-2 bg-destructive text-white text-sm font-medium rounded-lg hover:bg-destructive/90">
                  Отклонить
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </motion.div>
    </div>
  );
}
