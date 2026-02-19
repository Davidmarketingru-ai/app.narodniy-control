import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Bell, CheckCircle2, Award, ShieldCheck, MessageSquare,
  Clock, Check, Loader2
} from 'lucide-react';
import { notificationsApi } from '../lib/api';
import { Link } from 'react-router-dom';

const typeConfig = {
  review_created: { icon: MessageSquare, color: 'text-blue-400', bg: 'bg-blue-500/10' },
  review_verified: { icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
  verification_received: { icon: ShieldCheck, color: 'text-yellow-400', bg: 'bg-yellow-500/10' },
  points_earned: { icon: Award, color: 'text-primary', bg: 'bg-primary/10' },
  reward_redeemed: { icon: Award, color: 'text-purple-400', bg: 'bg-purple-500/10' },
};

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    notificationsApi.list().then(setNotifications).catch(console.error).finally(() => setLoading(false));
  }, []);

  const handleMarkAllRead = async () => {
    await notificationsApi.markAllRead();
    setNotifications(notifications.map(n => ({ ...n, is_read: true })));
  };

  const handleMarkRead = async (id) => {
    await notificationsApi.markRead(id);
    setNotifications(notifications.map(n => n.notification_id === id ? { ...n, is_read: true } : n));
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="max-w-2xl mx-auto" data-testid="notifications-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight" style={{ fontFamily: 'Manrope' }}>
              Уведомления
            </h1>
            {unreadCount > 0 && (
              <p className="text-sm text-muted-foreground mt-1">{unreadCount} непрочитанных</p>
            )}
          </div>
          {unreadCount > 0 && (
            <button
              onClick={handleMarkAllRead}
              data-testid="mark-all-read-btn"
              className="text-sm text-primary hover:underline flex items-center gap-1"
            >
              <Check className="w-4 h-4" />
              Прочитать все
            </button>
          )}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : notifications.length === 0 ? (
          <div className="glass rounded-xl p-8 text-center">
            <Bell className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
            <p className="text-muted-foreground">Уведомлений пока нет</p>
          </div>
        ) : (
          <div className="space-y-2">
            {notifications.map((notif, i) => {
              const config = typeConfig[notif.type] || typeConfig.review_created;
              const Icon = config.icon;
              return (
                <motion.div
                  key={notif.notification_id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  onClick={() => !notif.is_read && handleMarkRead(notif.notification_id)}
                  className={`glass rounded-xl p-4 flex items-start gap-3 cursor-pointer transition-all hover:border-primary/20 ${!notif.is_read ? 'border-l-2 border-l-primary' : 'opacity-70'}`}
                  data-testid={`notification-${notif.notification_id}`}
                >
                  <div className={`w-10 h-10 rounded-xl ${config.bg} flex items-center justify-center shrink-0`}>
                    <Icon className={`w-5 h-5 ${config.color}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className={`text-sm font-semibold ${!notif.is_read ? 'text-foreground' : 'text-muted-foreground'}`}>
                      {notif.title}
                    </h3>
                    {notif.message && (
                      <p className="text-sm text-muted-foreground mt-0.5 line-clamp-2">{notif.message}</p>
                    )}
                    <p className="text-xs text-muted-foreground mt-1 font-mono">
                      {new Date(notif.created_at).toLocaleString('ru-RU')}
                    </p>
                  </div>
                  {!notif.is_read && (
                    <div className="w-2 h-2 rounded-full bg-primary shrink-0 mt-2" />
                  )}
                </motion.div>
              );
            })}
          </div>
        )}
      </motion.div>
    </div>
  );
}
