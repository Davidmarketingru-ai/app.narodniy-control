import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield, ShieldCheck, Phone, CreditCard, UserCheck,
  ChevronRight, Loader2, Check, AlertCircle, Lock, Fingerprint
} from 'lucide-react';
import { verificationApi } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

const bankOptions = [
  { id: 'sber', name: 'Сбер ID', color: '#21a038' },
  { id: 'tinkoff', name: 'Тинькофф ID', color: '#ffdd2d' },
  { id: 'vtb', name: 'ВТБ ID', color: '#002882' },
  { id: 'alfa', name: 'Альфа ID', color: '#ef3124' },
];

export default function VerificationPage() {
  const { refreshUser } = useAuth();
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeStep, setActiveStep] = useState(null);
  // Phone
  const [phone, setPhone] = useState('');
  const [phoneCode, setPhoneCode] = useState('');
  const [phoneSent, setPhoneSent] = useState(false);
  const [phoneMsg, setPhoneMsg] = useState('');
  // Passport
  const [passFullName, setPassFullName] = useState('');
  const [passBirth, setPassBirth] = useState('');
  const [passSeries, setPassSeries] = useState('');
  const [passNumber, setPassNumber] = useState('');
  const [passMsg, setPassMsg] = useState('');
  // General
  const [actionLoading, setActionLoading] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    verificationApi.status().then(setStatus).catch(console.error).finally(() => setLoading(false));
  }, []);

  const handleSendPhone = async () => {
    setActionLoading(true); setPhoneMsg('');
    try {
      const res = await verificationApi.sendPhoneCode(phone);
      setPhoneSent(true); setPhoneMsg(res.message);
    } catch (e) { setPhoneMsg(e.response?.data?.detail || 'Ошибка'); }
    finally { setActionLoading(false); }
  };

  const handleConfirmPhone = async () => {
    setActionLoading(true); setPhoneMsg('');
    try {
      await verificationApi.confirmPhone(phoneCode);
      setPhoneMsg('Телефон подтверждён!');
      await refreshUser();
      const s = await verificationApi.status(); setStatus(s);
      setActiveStep(null);
    } catch (e) { setPhoneMsg(e.response?.data?.detail || 'Неверный код'); }
    finally { setActionLoading(false); }
  };

  const handlePassport = async () => {
    setActionLoading(true); setPassMsg('');
    try {
      await verificationApi.verifyPassport({ full_name: passFullName, birth_date: passBirth, series: passSeries, number: passNumber });
      setPassMsg('Паспорт верифицирован!');
      await refreshUser();
      const s = await verificationApi.status(); setStatus(s);
      setActiveStep(null);
    } catch (e) { setPassMsg(e.response?.data?.detail || 'Ошибка'); }
    finally { setActionLoading(false); }
  };

  const handleBankId = async (bank) => {
    setActionLoading(true); setMsg('');
    try {
      const res = await verificationApi.verifyBankId(bank);
      setMsg(res.message);
      await refreshUser();
      const s = await verificationApi.status(); setStatus(s);
    } catch (e) { setMsg(e.response?.data?.detail || 'Ошибка'); }
    finally { setActionLoading(false); }
  };

  const handleYandexId = async () => {
    setActionLoading(true); setMsg('');
    try {
      await verificationApi.verifyYandexId();
      setMsg('Яндекс ID подтверждён!');
      await refreshUser();
      const s = await verificationApi.status(); setStatus(s);
    } catch (e) { setMsg(e.response?.data?.detail || 'Ошибка'); }
    finally { setActionLoading(false); }
  };

  if (loading) return <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;

  const levelConfig = {
    basic: { icon: Shield, color: '#6b7280', label: 'Базовый' },
    confirmed: { icon: ShieldCheck, color: '#3b82f6', label: 'Подтверждённый' },
    verified: { icon: Fingerprint, color: '#10b981', label: 'Верифицированный' },
  };
  const cur = levelConfig[status?.level || 'basic'];
  const CurIcon = cur.icon;

  return (
    <div className="max-w-2xl mx-auto" data-testid="verification-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold tracking-tight mb-2" style={{ fontFamily: 'Manrope' }}>Верификация</h1>
        <p className="text-muted-foreground mb-6">Подтвердите личность для доступа ко всем функциям</p>

        {/* Current Level */}
        <div className="glass rounded-xl p-6 mb-6 flex items-center gap-4" data-testid="verification-level">
          <div className="w-16 h-16 rounded-2xl flex items-center justify-center" style={{ backgroundColor: cur.color + '20' }}>
            <CurIcon className="w-8 h-8" style={{ color: cur.color }} />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Текущий уровень</p>
            <p className="text-xl font-bold" style={{ color: cur.color }}>{cur.label}</p>
          </div>
        </div>

        {/* Level Progress */}
        <div className="flex gap-2 mb-8">
          {Object.entries(levelConfig).map(([key, cfg]) => {
            const active = key === status?.level;
            const done = ['basic', 'confirmed', 'verified'].indexOf(key) <= ['basic', 'confirmed', 'verified'].indexOf(status?.level || 'basic');
            return (
              <div key={key} className={`flex-1 rounded-xl p-3 text-center border transition-all ${active ? 'border-current glass' : done ? 'glass opacity-60' : 'glass opacity-30'}`} style={active ? { borderColor: cfg.color } : {}}>
                <cfg.icon className="w-5 h-5 mx-auto mb-1" style={{ color: cfg.color }} />
                <p className="text-xs font-medium" style={{ color: done ? cfg.color : undefined }}>{cfg.label}</p>
              </div>
            );
          })}
        </div>

        {msg && <div className="glass rounded-lg p-3 mb-4 text-sm text-emerald-400 flex items-center gap-2"><Check className="w-4 h-4" />{msg}</div>}

        {/* Phone Verification */}
        <div className="glass rounded-xl p-6 mb-4">
          <button onClick={() => setActiveStep(activeStep === 'phone' ? null : 'phone')} className="w-full flex items-center justify-between" data-testid="verify-phone-toggle">
            <div className="flex items-center gap-3">
              <Phone className="w-5 h-5 text-primary" />
              <span className="font-medium text-foreground">Телефон</span>
            </div>
            <div className="flex items-center gap-2">
              {status?.phone_verified ? <Check className="w-5 h-5 text-emerald-400" /> : <ChevronRight className={`w-4 h-4 text-muted-foreground transition-transform ${activeStep === 'phone' ? 'rotate-90' : ''}`} />}
            </div>
          </button>
          <AnimatePresence>
            {activeStep === 'phone' && !status?.phone_verified && (
              <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                <div className="pt-4 space-y-3">
                  {!phoneSent ? (
                    <>
                      <input type="tel" value={phone} onChange={e => setPhone(e.target.value)} placeholder="+7 (999) 123-45-67" data-testid="phone-input"
                        className="w-full bg-secondary/50 border border-transparent focus:border-primary rounded-xl h-12 px-4 text-foreground placeholder:text-muted-foreground outline-none" />
                      <button onClick={handleSendPhone} disabled={actionLoading || phone.length < 10} data-testid="send-phone-code-btn"
                        className="w-full bg-primary text-primary-foreground py-3 rounded-xl font-medium disabled:opacity-50 flex items-center justify-center gap-2">
                        {actionLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Отправить код'}
                      </button>
                    </>
                  ) : (
                    <>
                      <input type="text" value={phoneCode} onChange={e => setPhoneCode(e.target.value)} placeholder="Код из SMS" maxLength={6} data-testid="phone-code-input"
                        className="w-full bg-secondary/50 border border-transparent focus:border-primary rounded-xl h-12 px-4 text-foreground text-center font-mono text-xl tracking-widest placeholder:text-muted-foreground outline-none" />
                      <button onClick={handleConfirmPhone} disabled={actionLoading || phoneCode.length < 4} data-testid="confirm-phone-btn"
                        className="w-full bg-primary text-primary-foreground py-3 rounded-xl font-medium disabled:opacity-50 flex items-center justify-center gap-2">
                        {actionLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Подтвердить'}
                      </button>
                    </>
                  )}
                  {phoneMsg && <p className={`text-sm ${phoneMsg.includes('Ошибка') || phoneMsg.includes('Неверный') ? 'text-destructive' : 'text-emerald-400'}`}>{phoneMsg}</p>}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Passport Verification */}
        <div className="glass rounded-xl p-6 mb-4">
          <button onClick={() => setActiveStep(activeStep === 'passport' ? null : 'passport')} className="w-full flex items-center justify-between" data-testid="verify-passport-toggle">
            <div className="flex items-center gap-3">
              <UserCheck className="w-5 h-5 text-emerald-400" />
              <span className="font-medium text-foreground">Паспорт РФ</span>
            </div>
            {status?.passport_verified ? <Check className="w-5 h-5 text-emerald-400" /> : <ChevronRight className={`w-4 h-4 text-muted-foreground transition-transform ${activeStep === 'passport' ? 'rotate-90' : ''}`} />}
          </button>
          <AnimatePresence>
            {activeStep === 'passport' && !status?.passport_verified && (
              <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                <div className="pt-4 space-y-3">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground bg-secondary/50 rounded-lg p-2"><Lock className="w-3 h-3" />Данные шифруются и хранятся в виде хэша</div>
                  <input type="text" value={passFullName} onChange={e => setPassFullName(e.target.value)} placeholder="ФИО полностью" data-testid="passport-name-input"
                    className="w-full bg-secondary/50 border border-transparent focus:border-primary rounded-xl h-12 px-4 text-foreground placeholder:text-muted-foreground outline-none" />
                  <input type="date" value={passBirth} onChange={e => setPassBirth(e.target.value)} data-testid="passport-birth-input"
                    className="w-full bg-secondary/50 border border-transparent focus:border-primary rounded-xl h-12 px-4 text-foreground outline-none" />
                  <div className="grid grid-cols-2 gap-3">
                    <input type="text" value={passSeries} onChange={e => setPassSeries(e.target.value.replace(/\D/g,'').slice(0,4))} placeholder="Серия (4 цифры)" maxLength={4} data-testid="passport-series-input"
                      className="bg-secondary/50 border border-transparent focus:border-primary rounded-xl h-12 px-4 text-foreground font-mono text-center placeholder:text-muted-foreground outline-none" />
                    <input type="text" value={passNumber} onChange={e => setPassNumber(e.target.value.replace(/\D/g,'').slice(0,6))} placeholder="Номер (6 цифр)" maxLength={6} data-testid="passport-number-input"
                      className="bg-secondary/50 border border-transparent focus:border-primary rounded-xl h-12 px-4 text-foreground font-mono text-center placeholder:text-muted-foreground outline-none" />
                  </div>
                  <button onClick={handlePassport} disabled={actionLoading || !passFullName || !passBirth || passSeries.length !== 4 || passNumber.length !== 6} data-testid="verify-passport-btn"
                    className="w-full bg-emerald-600 text-white py-3 rounded-xl font-medium disabled:opacity-50 flex items-center justify-center gap-2">
                    {actionLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Верифицировать'}
                  </button>
                  {passMsg && <p className={`text-sm ${passMsg.includes('Ошибка') || passMsg.includes('Некорректн') || passMsg.includes('уже') ? 'text-destructive' : 'text-emerald-400'}`}>{passMsg}</p>}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Bank ID */}
        <div className="glass rounded-xl p-6 mb-4">
          <button onClick={() => setActiveStep(activeStep === 'bank' ? null : 'bank')} className="w-full flex items-center justify-between" data-testid="verify-bank-toggle">
            <div className="flex items-center gap-3">
              <CreditCard className="w-5 h-5 text-blue-400" />
              <span className="font-medium text-foreground">Банк ID</span>
            </div>
            {status?.bank_id_verified ? <Check className="w-5 h-5 text-emerald-400" /> : <ChevronRight className={`w-4 h-4 text-muted-foreground transition-transform ${activeStep === 'bank' ? 'rotate-90' : ''}`} />}
          </button>
          <AnimatePresence>
            {activeStep === 'bank' && !status?.bank_id_verified && (
              <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                <div className="pt-4 grid grid-cols-2 gap-3">
                  {bankOptions.map(b => (
                    <button key={b.id} onClick={() => handleBankId(b.id)} disabled={actionLoading} data-testid={`bank-id-${b.id}`}
                      className="p-4 rounded-xl border border-border/50 hover:border-primary/30 transition-all text-center"
                      style={{ borderLeftColor: b.color, borderLeftWidth: '3px' }}>
                      <p className="font-medium text-foreground text-sm">{b.name}</p>
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Yandex ID */}
        <div className="glass rounded-xl p-6 mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-5 h-5 rounded bg-red-500 flex items-center justify-center"><span className="text-white text-xs font-bold">Y</span></div>
              <span className="font-medium text-foreground">Яндекс ID</span>
            </div>
            {status?.yandex_id_verified ? (
              <Check className="w-5 h-5 text-emerald-400" />
            ) : (
              <button onClick={handleYandexId} disabled={actionLoading} data-testid="verify-yandex-btn"
                className="px-4 py-2 bg-red-500 text-white text-sm font-medium rounded-lg hover:bg-red-600 disabled:opacity-50">
                {actionLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Подключить'}
              </button>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
