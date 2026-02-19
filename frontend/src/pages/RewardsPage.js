import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Award, ShoppingBag, Coffee, Truck, Pill, Dumbbell,
  Scale, Stethoscope, ShoppingCart, Package, Film,
  ShieldCheck, Utensils, Loader2
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { rewardsApi } from '../lib/api';

const iconMap = {
  film: Film,
  coffee: Coffee,
  truck: Truck,
  utensils: Utensils,
  scale: Scale,
  dumbbell: Dumbbell,
  pill: Pill,
  stethoscope: Stethoscope,
  'shopping-cart': ShoppingCart,
  'package': Package,
  'shield-check': ShieldCheck,
};

export default function RewardsPage() {
  const { user, refreshUser } = useAuth();
  const [rewards, setRewards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [redeeming, setRedeeming] = useState(null);

  useEffect(() => {
    rewardsApi.list(user?.age_group).then(setRewards).catch(console.error).finally(() => setLoading(false));
  }, [user?.age_group]);

  const handleRedeem = async (reward) => {
    if ((user?.points || 0) < reward.price) return;
    setRedeeming(reward.reward_id);
    try {
      await rewardsApi.redeem(reward.reward_id);
      await refreshUser();
    } catch (err) {
      console.error(err);
    } finally {
      setRedeeming(null);
    }
  };

  const ageGroupLabel = {
    '18-25': '18-25 лет',
    '26-40': '26-40 лет',
    '41-60': '41-60 лет',
    '60+': '60+ лет',
  };

  return (
    <div className="max-w-2xl mx-auto" data-testid="rewards-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold tracking-tight mb-1" style={{ fontFamily: 'Manrope' }}>
          Магазин наград
        </h1>
        <p className="text-muted-foreground mb-6">
          Для группы: {ageGroupLabel[user?.age_group] || '26-40 лет'}
        </p>

        {/* Balance */}
        <div className="bg-gradient-to-r from-primary/20 to-primary/5 border border-primary/20 rounded-xl p-6 mb-6" data-testid="rewards-balance">
          <div className="flex items-center gap-2 mb-2">
            <Award className="w-5 h-5 text-primary" />
            <span className="text-sm text-muted-foreground uppercase tracking-wider">Ваши баллы</span>
          </div>
          <p className="text-4xl font-bold text-primary font-mono">{user?.points || 0}</p>
        </div>

        {/* Rewards Grid */}
        {loading ? (
          <div className="space-y-3">
            {[1,2,3].map(i => (
              <div key={i} className="glass rounded-xl p-5 animate-pulse">
                <div className="flex gap-4">
                  <div className="w-14 h-14 bg-muted rounded-xl" />
                  <div className="flex-1">
                    <div className="h-4 bg-muted rounded w-1/2 mb-2" />
                    <div className="h-3 bg-muted rounded w-3/4" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {rewards.map((reward, i) => {
              const Icon = iconMap[reward.icon] || ShoppingBag;
              const canAfford = (user?.points || 0) >= reward.price;
              return (
                <motion.div
                  key={reward.reward_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="glass rounded-xl p-5"
                  data-testid={`reward-${reward.reward_id}`}
                >
                  <div className="flex items-start gap-4">
                    <div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center shrink-0">
                      <Icon className="w-7 h-7 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-foreground">{reward.name}</h3>
                      <p className="text-sm text-muted-foreground mb-3">{reward.description}</p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5">
                          <Award className="w-4 h-4 text-primary" />
                          <span className="font-bold text-primary font-mono">{reward.price}</span>
                          <span className="text-xs text-muted-foreground">баллов</span>
                        </div>
                        <button
                          onClick={() => handleRedeem(reward)}
                          disabled={!canAfford || redeeming === reward.reward_id}
                          data-testid={`redeem-${reward.reward_id}`}
                          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                            canAfford
                              ? 'bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_0_10px_rgba(59,130,246,0.2)]'
                              : 'bg-secondary text-muted-foreground cursor-not-allowed'
                          }`}
                        >
                          {redeeming === reward.reward_id ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            'Обменять'
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </motion.div>
    </div>
  );
}
