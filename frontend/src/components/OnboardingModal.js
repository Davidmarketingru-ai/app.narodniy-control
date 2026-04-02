import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, MapPin, Star, Users, ArrowRight, Check, Sparkles } from 'lucide-react';
import { onboardingApi } from '../lib/api';

const STEPS = [
  {
    title: 'Добро пожаловать!',
    desc: 'Народный Контроль — платформа, где граждане вместе делают город лучше. Ваши отзывы помогают другим людям.',
    icon: Shield,
    color: '#3b82f6',
  },
  {
    title: 'Как это работает',
    desc: 'Вы создаёте отзыв о заведении — другие пользователи проверяют его. После 2 подтверждений отзыв публикуется, а вы получаете баллы.',
    icon: Star,
    color: '#eab308',
  },
  {
    title: 'Зарабатывайте баллы',
    desc: 'Баллы за отзывы, верификацию и ежедневные миссии. Обменивайте баллы на награды в магазине. Приглашайте друзей — получайте бонусы!',
    icon: Sparkles,
    color: '#10b981',
  },
];

export default function OnboardingModal({ onComplete }) {
  const [step, setStep] = useState(0);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    onboardingApi.status().then(data => {
      if (!data.completed) setVisible(true);
    }).catch(() => {});
  }, []);

  const handleNext = () => {
    if (step < STEPS.length - 1) {
      setStep(step + 1);
      onboardingApi.complete({ step: step + 1 }).catch(() => {});
    } else {
      onboardingApi.complete({ step: STEPS.length, completed: true }).catch(() => {});
      setVisible(false);
      onComplete?.();
    }
  };

  const handleSkip = () => {
    onboardingApi.complete({ step: STEPS.length, completed: true }).catch(() => {});
    setVisible(false);
    onComplete?.();
  };

  if (!visible) return null;

  const current = STEPS[step];
  const Icon = current.icon;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[100] p-4" data-testid="onboarding-modal">
        <motion.div
          key={step}
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          className="glass rounded-2xl p-8 max-w-md w-full text-center"
        >
          <motion.div
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.15, type: 'spring' }}
            className="w-20 h-20 rounded-2xl mx-auto mb-6 flex items-center justify-center"
            style={{ backgroundColor: current.color + '20' }}
          >
            <Icon className="w-10 h-10" style={{ color: current.color }} />
          </motion.div>

          <h2 className="text-2xl font-bold text-foreground mb-3" style={{ fontFamily: 'Manrope' }}>
            {current.title}
          </h2>
          <p className="text-muted-foreground text-sm leading-relaxed mb-8">
            {current.desc}
          </p>

          {/* Progress dots */}
          <div className="flex items-center justify-center gap-2 mb-6">
            {STEPS.map((_, i) => (
              <div key={i} className={`h-1.5 rounded-full transition-all duration-300 ${
                i === step ? 'w-8 bg-primary' : i < step ? 'w-4 bg-primary/40' : 'w-4 bg-muted-foreground/20'
              }`} />
            ))}
          </div>

          <div className="flex gap-3">
            <button onClick={handleSkip} data-testid="onboarding-skip-btn"
              className="flex-1 py-3 text-sm text-muted-foreground hover:text-foreground transition-colors">
              Пропустить
            </button>
            <button onClick={handleNext} data-testid="onboarding-next-btn"
              className="flex-1 bg-primary text-primary-foreground py-3 rounded-xl text-sm font-medium flex items-center justify-center gap-2 hover:bg-primary/90 transition-all">
              {step < STEPS.length - 1 ? (
                <>Далее <ArrowRight className="w-4 h-4" /></>
              ) : (
                <>Начать! <Check className="w-4 h-4" /></>
              )}
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
