import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users, Plus, X, Loader2, ChevronRight, MessageSquare,
  Crown, UserPlus, LogOut, Send, ArrowLeft, Newspaper,
  Vote, ShieldCheck, AlertTriangle, CheckCircle2, Clock,
  ThumbsUp, Eye, Ban, FileText, ArrowUpCircle, Home
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { councilsApi } from '../lib/api';

const LEVEL_CONFIG = {
  yard: { name: 'Дворовый', color: '#10b981' },
  district: { name: 'Районный', color: '#3b82f6' },
  city: { name: 'Городской', color: '#8b5cf6' },
  republic: { name: 'Республиканский', color: '#f59e0b' },
  country: { name: 'Народный', color: '#ef4444' },
};

const DISC_CATEGORIES = [
  { id: 'general', label: 'Общее' },
  { id: 'problem', label: 'Проблема' },
  { id: 'proposal', label: 'Предложение' },
  { id: 'budget', label: 'Бюджет' },
  { id: 'event', label: 'Мероприятие' },
];

const AI_LABELS = {
  high: { text: 'Достоверно', color: '#10b981', icon: CheckCircle2 },
  medium: { text: 'Требует проверки', color: '#f59e0b', icon: Eye },
  low: { text: 'Подозрительно', color: '#f97316', icon: AlertTriangle },
  fake: { text: 'Дезинформация', color: '#ef4444', icon: Ban },
};

function ConfirmationBar({ council }) {
  const count = council.confirmations?.length || 0;
  const needed = council.confirmations_needed || 10;
  const pct = Math.min((count / needed) * 100, 100);
  return (
    <div className="mt-3" data-testid="confirmation-bar">
      <div className="flex items-center justify-between text-xs mb-1">
        <span className="text-muted-foreground">Подтверждений: {count}/{needed}</span>
        {council.confirmed && <span className="text-green-400 font-medium flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> Активен</span>}
        {!council.confirmed && <span className="text-yellow-400 font-medium flex items-center gap-1"><Clock className="w-3 h-3" /> Ожидание</span>}
      </div>
      <div className="w-full bg-secondary/50 rounded-full h-2 overflow-hidden">
        <div className="h-full rounded-full transition-all duration-500" style={{ width: `${pct}%`, backgroundColor: council.confirmed ? '#10b981' : '#f59e0b' }} />
      </div>
    </div>
  );
}

function FormationBar({ councilId }) {
  const [info, setInfo] = useState(null);
  useEffect(() => {
    councilsApi.formation(councilId).then(setInfo).catch(() => {});
  }, [councilId]);
  if (!info || info.total_verified === 0) return null;
  return (
    <div className="mt-3" data-testid="formation-bar">
      <div className="flex items-center justify-between text-xs mb-1">
        <span className="text-muted-foreground">Формирование: {info.member_count}/{info.total_verified} жителей ({info.percent}%)</span>
        {info.formed ? (
          <span className="text-green-400 font-medium flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> Сформирован</span>
        ) : (
          <span className="text-blue-400 font-medium">Нужно 80%</span>
        )}
      </div>
      <div className="w-full bg-secondary/50 rounded-full h-2 overflow-hidden">
        <div className="h-full rounded-full transition-all duration-500" style={{ width: `${Math.min(info.percent, 100)}%`, backgroundColor: info.formed ? '#10b981' : '#3b82f6' }} />
      </div>
    </div>
  );
}

// ======================== NEWS TAB ========================
function NewsTab({ council, user }) {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ title: '', content: '' });
  const [submitting, setSubmitting] = useState(false);

  const isRep = council.representatives?.some(r => r.user_id === user?.user_id);
  const isChairman = council.members?.some(m => m.user_id === user?.user_id && m.role === 'chairman');
  const canPost = isRep || isChairman;
  const canModerate = isRep || isChairman || user?.role === 'admin';

  const load = useCallback(async () => {
    setLoading(true);
    try { setNews(await councilsApi.news(council.council_id)); } catch {} finally { setLoading(false); }
  }, [council.council_id]);

  useEffect(() => { load(); }, [load]);

  const handleCreate = async () => {
    setSubmitting(true);
    try {
      await councilsApi.createNews(council.council_id, form);
      setForm({ title: '', content: '' });
      setShowCreate(false);
      load();
    } catch (e) { alert(e.response?.data?.detail || 'Ошибка'); }
    finally { setSubmitting(false); }
  };

  const handleModerate = async (newsId, action) => {
    try { await councilsApi.moderateNews(council.council_id, newsId, { action }); load(); } catch {}
  };

  if (loading) return <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-primary" /></div>;

  return (
    <div data-testid="news-tab">
      {canPost && (
        <button onClick={() => setShowCreate(true)} data-testid="create-news-btn"
          className="w-full glass rounded-xl p-4 mb-4 text-left flex items-center gap-3 hover:border-primary/30 transition-all">
          <Newspaper className="w-5 h-5 text-primary" />
          <span className="text-sm text-muted-foreground">Опубликовать новость совета...</span>
        </button>
      )}
      {news.length === 0 && <p className="text-center text-muted-foreground text-sm py-6">Новостей пока нет</p>}
      {news.map(n => {
        const aiResult = n.ai_check?.result;
        const aiLabel = aiResult ? AI_LABELS[aiResult.credibility] : null;
        const AiIcon = aiLabel?.icon;
        return (
          <div key={n.news_id} className="glass rounded-xl p-5 mb-3" data-testid={`news-${n.news_id}`}>
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              {n.status === 'verified' && <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/20 text-green-400">Проверено</span>}
              {n.status === 'pending_moderation' && <span className="text-[10px] px-1.5 py-0.5 rounded bg-yellow-500/20 text-yellow-400">На модерации</span>}
              {n.status === 'rejected' && <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-500/20 text-red-400">Отклонено</span>}
            </div>
            <h4 className="font-semibold text-foreground text-sm">{n.title}</h4>
            <p className="text-xs text-muted-foreground mt-1 whitespace-pre-line">{n.content}</p>
            <p className="text-[10px] text-muted-foreground mt-2">{n.author_name} — {new Date(n.created_at).toLocaleDateString('ru-RU')}</p>
            {aiLabel && (
              <div className="mt-3 p-2.5 rounded-lg border border-border/50 bg-secondary/20" data-testid={`ai-label-${n.news_id}`}>
                <div className="flex items-center gap-2 text-xs">
                  <AiIcon className="w-3.5 h-3.5" style={{ color: aiLabel.color }} />
                  <span style={{ color: aiLabel.color }} className="font-medium">AI: {aiLabel.text}</span>
                </div>
                {aiResult.summary && <p className="text-[10px] text-muted-foreground mt-1">{aiResult.summary}</p>}
              </div>
            )}
            {canModerate && n.status === 'pending_moderation' && (
              <div className="flex gap-2 mt-3">
                <button onClick={() => handleModerate(n.news_id, 'approve')} data-testid={`approve-news-${n.news_id}`}
                  className="text-xs px-3 py-1.5 rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/30">Одобрить</button>
                <button onClick={() => handleModerate(n.news_id, 'reject')} data-testid={`reject-news-${n.news_id}`}
                  className="text-xs px-3 py-1.5 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30">Отклонить</button>
              </div>
            )}
          </div>
        );
      })}
      <AnimatePresence>
        {showCreate && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowCreate(false)}>
            <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
              onClick={e => e.stopPropagation()} className="glass rounded-2xl p-6 w-full max-w-lg" data-testid="create-news-modal">
              <h2 className="text-lg font-bold mb-1">Новая новость совета</h2>
              <p className="text-xs text-muted-foreground mb-4">Будет проверена AI-модератором</p>
              <div className="space-y-3">
                <input type="text" value={form.title} onChange={e => setForm(p => ({ ...p, title: e.target.value }))}
                  placeholder="Заголовок (мин. 5 символов)" className="w-full bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" data-testid="news-title" />
                <textarea value={form.content} onChange={e => setForm(p => ({ ...p, content: e.target.value }))}
                  placeholder="Содержание (мин. 20 символов)..." rows={5}
                  className="w-full bg-secondary/50 rounded-xl p-3 text-sm text-foreground outline-none resize-none" data-testid="news-content" />
                <button onClick={handleCreate} disabled={submitting || form.title.length < 5 || form.content.length < 20} data-testid="submit-news"
                  className="w-full bg-primary text-primary-foreground py-3 rounded-xl font-medium disabled:opacity-50">
                  {submitting ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Опубликовать'}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ======================== NOMINATIONS TAB ========================
function NominationsTab({ council, user, onRefresh }) {
  const [nominations, setNominations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showComplaint, setShowComplaint] = useState(false);
  const [complaintForm, setComplaintForm] = useState({ repId: '', reason: '' });

  const isMember = council.members?.some(m => m.user_id === user?.user_id);
  const isChairman = council.members?.some(m => m.user_id === user?.user_id && m.role === 'chairman');

  const load = useCallback(async () => {
    setLoading(true);
    try { setNominations(await councilsApi.nominations(council.council_id)); } catch {} finally { setLoading(false); }
  }, [council.council_id]);

  useEffect(() => { load(); }, [load]);

  const handleNominate = async (userId) => {
    try {
      const res = await councilsApi.nominate(council.council_id, userId);
      alert(`Голос засчитан! Всего: ${res.nominee_votes}`);
      load();
    } catch (e) { alert(e.response?.data?.detail || 'Ошибка'); }
  };

  const handleElect = async () => {
    if (!window.confirm('Провести выборы представителей?')) return;
    try { await councilsApi.electReps(council.council_id); onRefresh(); load(); }
    catch (e) { alert(e.response?.data?.detail || 'Ошибка'); }
  };

  const handleComplaint = async () => {
    try {
      await councilsApi.complaint(council.council_id, complaintForm.repId, complaintForm.reason);
      setShowComplaint(false);
      setComplaintForm({ repId: '', reason: '' });
      alert('Жалоба отправлена');
    } catch (e) { alert(e.response?.data?.detail || 'Ошибка'); }
  };

  if (loading) return <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-primary" /></div>;

  return (
    <div data-testid="nominations-tab">
      {council.representatives?.length > 0 && (
        <div className="glass rounded-xl p-4 mb-4">
          <h3 className="text-sm font-medium text-foreground mb-3 flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-primary" /> Представители</h3>
          <div className="space-y-2">
            {council.representatives.map(rep => (
              <div key={rep.user_id} className="flex items-center justify-between bg-secondary/30 rounded-lg p-3" data-testid={`rep-${rep.user_id}`}>
                <div>
                  <p className="text-sm text-foreground font-medium">{rep.name}</p>
                  <p className="text-[10px] text-muted-foreground">{rep.votes} голосов</p>
                </div>
                {isMember && rep.user_id !== user?.user_id && (
                  <button onClick={() => { setComplaintForm({ repId: rep.user_id, reason: '' }); setShowComplaint(true); }}
                    data-testid={`complaint-${rep.user_id}`}
                    className="text-[10px] px-2 py-1 rounded bg-red-500/10 text-red-400 hover:bg-red-500/20">Жалоба</button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      {isChairman && nominations.length > 0 && (
        <button onClick={handleElect} data-testid="elect-reps-btn"
          className="w-full glass rounded-xl p-4 mb-4 text-center text-sm font-medium text-primary hover:border-primary/30 transition-all">
          Провести выборы представителей
        </button>
      )}
      <h3 className="text-sm font-medium text-muted-foreground mb-3">Номинации</h3>
      {nominations.length === 0 && <p className="text-center text-muted-foreground text-sm py-4">Номинаций пока нет</p>}
      {nominations.map(nom => (
        <div key={nom.user_id} className="glass rounded-xl p-4 mb-2 flex items-center justify-between" data-testid={`nom-${nom.user_id}`}>
          <div>
            <p className="text-sm text-foreground font-medium">{nom.name}</p>
            <p className="text-[10px] text-muted-foreground">{nom.votes} голосов | {nom.points} очков</p>
          </div>
          <span className="text-sm font-bold text-primary">{nom.votes}</span>
        </div>
      ))}
      {isMember && (
        <div className="mt-4">
          <h3 className="text-sm font-medium text-muted-foreground mb-3">Номинировать участника</h3>
          <div className="space-y-1.5">
            {(council.members || []).filter(m => m.user_id !== user?.user_id && m.role !== 'chairman').map(m => (
              <div key={m.user_id} className="flex items-center justify-between bg-secondary/20 rounded-lg p-2.5">
                <span className="text-xs text-foreground">{m.name || 'Участник'}</span>
                <button onClick={() => handleNominate(m.user_id)} data-testid={`nominate-${m.user_id}`}
                  className="text-[10px] px-2.5 py-1 rounded-lg bg-primary/10 text-primary hover:bg-primary/20">
                  <ThumbsUp className="w-3 h-3 inline mr-1" />Голос
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
      <AnimatePresence>
        {showComplaint && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowComplaint(false)}>
            <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
              onClick={e => e.stopPropagation()} className="glass rounded-2xl p-6 w-full max-w-md" data-testid="complaint-modal">
              <h2 className="text-lg font-bold mb-4">Жалоба на представителя</h2>
              <textarea value={complaintForm.reason} onChange={e => setComplaintForm(p => ({ ...p, reason: e.target.value }))}
                placeholder="Причина (мин. 10 символов)..." rows={4}
                className="w-full bg-secondary/50 rounded-xl p-3 text-sm text-foreground outline-none resize-none mb-3" data-testid="complaint-reason" />
              <button onClick={handleComplaint} disabled={complaintForm.reason.length < 10} data-testid="submit-complaint"
                className="w-full bg-red-500 text-white py-3 rounded-xl font-medium disabled:opacity-50">Отправить жалобу</button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ======================== ESCALATION TAB ========================
function EscalationTab({ council, user }) {
  const [escalations, setEscalations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showInit, setShowInit] = useState(false);
  const [initForm, setInitForm] = useState({ name: '', district: '', city: '' });
  const [submitting, setSubmitting] = useState(false);

  const isChairman = council.members?.some(m => m.user_id === user?.user_id && m.role === 'chairman');
  const isRep = council.members?.some(m => m.user_id === user?.user_id && m.role === 'representative');
  const canInitiate = isChairman || isRep;

  const load = useCallback(async () => {
    setLoading(true);
    try { setEscalations(await councilsApi.activeEscalations(council.level)); } catch {} finally { setLoading(false); }
  }, [council.level]);

  useEffect(() => { load(); }, [load]);

  const handleInitiate = async () => {
    setSubmitting(true);
    try {
      const res = await councilsApi.escalation(council.council_id, {
        name: initForm.name,
        district: initForm.district || council.district,
        city: initForm.city || council.city,
      });
      alert(`Голосование создано! ${res.eligible_count} советов могут проголосовать.`);
      setShowInit(false);
      load();
    } catch (e) { alert(e.response?.data?.detail || 'Ошибка'); }
    finally { setSubmitting(false); }
  };

  const handleVote = async (eid, vote) => {
    try {
      const res = await councilsApi.voteEscalation(eid, vote);
      if (res.status === 'completed') {
        alert(`Совет следующего уровня создан!`);
      } else {
        alert(`Голос принят. За: ${res.votes_for}/${res.majority} (нужно большинство)`);
      }
      load();
    } catch (e) { alert(e.response?.data?.detail || 'Ошибка'); }
  };

  if (loading) return <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-primary" /></div>;

  const LEVEL_NAMES = { yard: 'Дворовый', district: 'Районный', city: 'Городской', republic: 'Республиканский', country: 'Народный' };
  const NEXT_LEVEL = { yard: 'district', district: 'city', city: 'republic', republic: 'country' };
  const nextLevel = NEXT_LEVEL[council.level];

  return (
    <div data-testid="escalation-tab">
      {canInitiate && nextLevel && (
        <button onClick={() => setShowInit(true)} data-testid="initiate-escalation-btn"
          className="w-full glass rounded-xl p-4 mb-4 text-left flex items-center gap-3 hover:border-primary/30 transition-all">
          <ArrowUpCircle className="w-5 h-5 text-primary" />
          <div>
            <span className="text-sm text-foreground font-medium">Инициировать {LEVEL_NAMES[nextLevel]} совет</span>
            <p className="text-[10px] text-muted-foreground">Голосование среди советов вашего уровня</p>
          </div>
        </button>
      )}

      {escalations.length === 0 && <p className="text-center text-muted-foreground text-sm py-6">Активных голосований за эскалацию нет</p>}

      {escalations.map(e => {
        const totalEligible = e.eligible_council_ids?.length || 0;
        const votesFor = e.votes_for?.length || 0;
        const votesAgainst = e.votes_against?.length || 0;
        const majority = Math.floor(totalEligible / 2) + 1;
        const myCouncilVoted = e.votes_for?.includes(council.council_id) || e.votes_against?.includes(council.council_id);
        const isEligible = e.eligible_council_ids?.includes(council.council_id);
        return (
          <div key={e.escalation_id} className="glass rounded-xl p-5 mb-3" data-testid={`escalation-${e.escalation_id}`}>
            <div className="flex items-center gap-2 mb-2">
              <ArrowUpCircle className="w-4 h-4 text-primary" />
              <span className="text-xs px-2 py-0.5 rounded-full bg-primary/20 text-primary">
                {LEVEL_NAMES[e.source_level]} → {LEVEL_NAMES[e.target_level]}
              </span>
            </div>
            <h4 className="font-semibold text-foreground text-sm">{e.target_name}</h4>
            <p className="text-xs text-muted-foreground mt-1">Инициатор: {e.initiator_name}</p>
            <div className="mt-3">
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-muted-foreground">За: {votesFor}/{majority} (нужно большинство)</span>
                <span className="text-muted-foreground">Против: {votesAgainst}</span>
              </div>
              <div className="w-full bg-secondary/50 rounded-full h-2 overflow-hidden">
                <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${Math.min((votesFor / majority) * 100, 100)}%` }} />
              </div>
              <p className="text-[10px] text-muted-foreground mt-1">{totalEligible} советов в голосовании</p>
            </div>
            {isEligible && !myCouncilVoted && canInitiate && (
              <div className="flex gap-2 mt-3">
                <button onClick={() => handleVote(e.escalation_id, 'for')} data-testid={`vote-for-${e.escalation_id}`}
                  className="flex-1 text-xs py-2 rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/30 font-medium">За</button>
                <button onClick={() => handleVote(e.escalation_id, 'against')} data-testid={`vote-against-${e.escalation_id}`}
                  className="flex-1 text-xs py-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 font-medium">Против</button>
              </div>
            )}
            {myCouncilVoted && (
              <p className="text-xs text-green-400 mt-3 text-center">Ваш совет уже проголосовал</p>
            )}
          </div>
        );
      })}

      {/* Initiate Escalation Modal */}
      <AnimatePresence>
        {showInit && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowInit(false)}>
            <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
              onClick={e => e.stopPropagation()} className="glass rounded-2xl p-6 w-full max-w-lg" data-testid="escalation-modal">
              <h2 className="text-lg font-bold mb-1">Создать {LEVEL_NAMES[nextLevel]} совет</h2>
              <p className="text-xs text-muted-foreground mb-4">Голосование среди всех подходящих советов вашего уровня</p>
              <div className="space-y-3">
                <input type="text" value={initForm.name} onChange={e => setInitForm(p => ({ ...p, name: e.target.value }))}
                  placeholder={`Название ${LEVEL_NAMES[nextLevel]} совета`}
                  className="w-full bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" data-testid="escalation-name" />
                <input type="text" value={initForm.district || council.district || ''} onChange={e => setInitForm(p => ({ ...p, district: e.target.value }))}
                  placeholder="Район" className="w-full bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" />
                <input type="text" value={initForm.city || council.city || ''} onChange={e => setInitForm(p => ({ ...p, city: e.target.value }))}
                  placeholder="Город" className="w-full bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" />
                <button onClick={handleInitiate} disabled={submitting || !initForm.name} data-testid="submit-escalation"
                  className="w-full bg-primary text-primary-foreground py-3 rounded-xl font-medium disabled:opacity-50">
                  {submitting ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Начать голосование'}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ======================== MAIN PAGE ========================
export default function CouncilsPage() {
  const { user } = useAuth();
  const [councils, setCouncils] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterLevel, setFilterLevel] = useState('');
  const [selected, setSelected] = useState(null);
  const [discussions, setDiscussions] = useState([]);
  const [votes, setVotes] = useState([]);
  const [tab, setTab] = useState('discussions');
  const [showCreate, setShowCreate] = useState(false);
  const [showNewDisc, setShowNewDisc] = useState(false);
  const [showNewVote, setShowNewVote] = useState(false);
  const [form, setForm] = useState({ name: '', description: '', street: '', house_number: '', district: '', city: '', legal_consent: false });
  const [discForm, setDiscForm] = useState({ title: '', content: '', category: 'general' });
  const [voteForm, setVoteForm] = useState({ title: '', description: '', options: ['', ''] });
  const [submitting, setSubmitting] = useState(false);
  const [replyText, setReplyText] = useState({});
  const [openDisc, setOpenDisc] = useState(null);

  useEffect(() => { loadCouncils(); }, [filterLevel]);

  const loadCouncils = async () => {
    setLoading(true);
    try {
      const params = filterLevel ? { level: filterLevel } : {};
      setCouncils(await councilsApi.list(params));
    } catch {} finally { setLoading(false); }
  };

  const openCouncil = async (c) => {
    setSelected(c);
    try {
      const [d, v] = await Promise.all([
        councilsApi.discussions(c.council_id),
        councilsApi.votes(c.council_id),
      ]);
      setDiscussions(d);
      setVotes(v);
    } catch {}
    setTab('discussions');
  };

  const refreshCouncil = async () => {
    if (!selected) return;
    try { setSelected(await councilsApi.get(selected.council_id)); } catch {}
  };

  const isMember = selected?.members?.some(m => m.user_id === user?.user_id);
  const myRole = selected?.members?.find(m => m.user_id === user?.user_id)?.role;

  const handleCreate = async () => {
    setSubmitting(true);
    try {
      const res = await councilsApi.create(form);
      setCouncils(prev => [res, ...prev]);
      setShowCreate(false);
      setForm({ name: '', description: '', street: '', house_number: '', district: '', city: '', legal_consent: false });
    } catch (e) { alert(e.response?.data?.detail || 'Ошибка'); }
    finally { setSubmitting(false); }
  };

  const handleConfirm = async (councilId) => {
    try {
      const updated = await councilsApi.confirm(councilId);
      if (selected?.council_id === councilId) setSelected(updated);
      setCouncils(prev => prev.map(c => c.council_id === councilId ? updated : c));
    } catch (e) { alert(e.response?.data?.detail || 'Ошибка'); }
  };

  const handleJoin = async () => {
    try { await councilsApi.join(selected.council_id); refreshCouncil(); }
    catch (e) { alert(e.response?.data?.detail || 'Ошибка'); }
  };

  const handleLeave = async () => {
    try { await councilsApi.leave(selected.council_id); refreshCouncil(); }
    catch (e) { alert(e.response?.data?.detail || 'Ошибка'); }
  };

  const handleNewDisc = async () => {
    setSubmitting(true);
    try {
      await councilsApi.createDiscussion(selected.council_id, discForm);
      setDiscussions(await councilsApi.discussions(selected.council_id));
      setShowNewDisc(false);
      setDiscForm({ title: '', content: '', category: 'general' });
    } catch (e) { alert(e.response?.data?.detail || 'Ошибка'); }
    finally { setSubmitting(false); }
  };

  const handleReply = async (discId) => {
    const text = replyText[discId]?.trim();
    if (!text || text.length < 5) return;
    try {
      await councilsApi.replyDiscussion(selected.council_id, discId, text);
      setDiscussions(await councilsApi.discussions(selected.council_id));
      setReplyText(prev => ({ ...prev, [discId]: '' }));
    } catch {}
  };

  const handleNewVote = async () => {
    const opts = voteForm.options.filter(o => o.trim());
    if (opts.length < 2) return;
    setSubmitting(true);
    try {
      await councilsApi.createVote(selected.council_id, { ...voteForm, options: opts });
      setVotes(await councilsApi.votes(selected.council_id));
      setShowNewVote(false);
      setVoteForm({ title: '', description: '', options: ['', ''] });
    } catch (e) { alert(e.response?.data?.detail || 'Ошибка'); }
    finally { setSubmitting(false); }
  };

  const handleCastVote = async (voteId, optionId) => {
    try {
      await councilsApi.castVote(selected.council_id, voteId, optionId);
      setVotes(await councilsApi.votes(selected.council_id));
    } catch (e) { alert(e.response?.data?.detail || 'Уже проголосовали'); }
  };

  // ======================== DETAIL VIEW ========================
  if (selected) {
    const lvl = LEVEL_CONFIG[selected.level] || LEVEL_CONFIG.yard;
    const isPending = !selected.confirmed;
    const alreadyConfirmed = selected.confirmations?.some(c => c.user_id === user?.user_id);
    const isCreator = selected.created_by === user?.user_id;
    const isFormedViaEscalation = !!selected.formed_via_escalation;

    return (
      <div className="max-w-3xl mx-auto" data-testid="council-detail">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <button onClick={() => setSelected(null)} className="flex items-center gap-2 text-sm text-muted-foreground mb-4 hover:text-foreground" data-testid="back-btn">
            <ArrowLeft className="w-4 h-4" /> Все советы
          </button>

          <div className="glass rounded-xl p-6 mb-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1 flex-wrap">
                  <span className="text-xs px-2 py-0.5 rounded-full text-white" style={{ backgroundColor: lvl.color }}>{lvl.name}</span>
                  {isPending && <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-500/20 text-yellow-400">Ожидает подтверждения</span>}
                  {!isPending && <span className="text-xs px-2 py-0.5 rounded-full bg-green-500/20 text-green-400">Активен</span>}
                  {isFormedViaEscalation && <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400">Сформирован голосованием</span>}
                </div>
                <h2 className="text-xl font-bold text-foreground mt-1">{selected.name}</h2>
                <p className="text-sm text-muted-foreground mt-1">{selected.description}</p>
                {selected.address && <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1"><Home className="w-3 h-3" /> {selected.address}</p>}
                <p className="text-xs text-muted-foreground mt-1 font-mono">{selected.member_count} участников</p>
              </div>
              <div className="flex flex-col items-end gap-2">
                {!isMember ? (
                  <button onClick={handleJoin} data-testid="join-council-btn"
                    className="bg-primary text-primary-foreground px-4 py-2 rounded-xl text-sm flex items-center gap-2">
                    <UserPlus className="w-4 h-4" /> Вступить
                  </button>
                ) : myRole !== 'chairman' ? (
                  <button onClick={handleLeave} className="text-xs text-muted-foreground hover:text-destructive px-3 py-1.5 glass rounded-lg flex items-center gap-1">
                    <LogOut className="w-3 h-3" /> Выйти
                  </button>
                ) : (
                  <span className="text-xs px-2 py-1 rounded-lg bg-yellow-500/10 text-yellow-400 flex items-center gap-1">
                    <Crown className="w-3 h-3" /> Председатель
                  </span>
                )}
              </div>
            </div>

            {isPending && <ConfirmationBar council={selected} />}
            {selected.level === 'yard' && selected.confirmed && <FormationBar councilId={selected.council_id} />}

            {isPending && !alreadyConfirmed && !isCreator && (
              <button onClick={() => handleConfirm(selected.council_id)} data-testid="confirm-council-btn"
                className="mt-3 w-full bg-yellow-500/20 text-yellow-400 py-2.5 rounded-xl text-sm font-medium hover:bg-yellow-500/30 transition-all flex items-center justify-center gap-2">
                <CheckCircle2 className="w-4 h-4" /> Подтвердить создание совета
              </button>
            )}
            {isPending && alreadyConfirmed && <p className="mt-3 text-xs text-green-400 text-center">Вы уже подтвердили</p>}
            {isPending && isCreator && <p className="mt-3 text-xs text-muted-foreground text-center">Ожидайте подтверждений от других</p>}
          </div>

          {/* Members */}
          <div className="glass rounded-xl p-4 mb-4">
            <h3 className="text-sm font-medium text-muted-foreground mb-2">Участники ({selected.members?.length || 0})</h3>
            <div className="flex flex-wrap gap-2">
              {(selected.members || []).slice(0, 20).map(m => (
                <div key={m.user_id} className="flex items-center gap-1.5 bg-secondary/50 px-2.5 py-1 rounded-lg">
                  <span className="text-xs text-foreground">{m.name || 'Участник'}</span>
                  {m.role === 'chairman' && <Crown className="w-3 h-3 text-yellow-400" />}
                  {m.role === 'representative' && <ShieldCheck className="w-3 h-3 text-blue-400" />}
                </div>
              ))}
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-1 glass rounded-xl p-1 mb-4 overflow-x-auto">
            {[
              { id: 'discussions', label: 'Обсуждения', icon: MessageSquare },
              { id: 'votes', label: 'Голосования', icon: Vote },
              { id: 'news', label: 'Новости', icon: Newspaper },
              { id: 'nominations', label: 'Представители', icon: ShieldCheck },
              { id: 'escalation', label: 'Эскалация', icon: ArrowUpCircle },
            ].map(t => (
              <button key={t.id} onClick={() => setTab(t.id)} data-testid={`tab-${t.id}`}
                className={`flex-1 py-2.5 rounded-lg text-xs font-medium transition-all flex items-center justify-center gap-1 whitespace-nowrap px-2 ${tab === t.id ? 'bg-primary text-primary-foreground' : 'text-muted-foreground'}`}>
                <t.icon className="w-3.5 h-3.5" /> {t.label}
              </button>
            ))}
          </div>

          {tab === 'discussions' && (
            <>
              {isMember && (
                <button onClick={() => setShowNewDisc(true)} data-testid="new-discussion-btn"
                  className="w-full glass rounded-xl p-4 mb-4 text-left flex items-center gap-3 hover:border-primary/30 transition-all">
                  <Plus className="w-5 h-5 text-primary" />
                  <span className="text-sm text-muted-foreground">Создать обсуждение...</span>
                </button>
              )}
              {discussions.length === 0 && <p className="text-center text-muted-foreground text-sm py-6">Обсуждений пока нет</p>}
              {discussions.map(d => {
                const isOpen = openDisc === d.discussion_id;
                return (
                  <div key={d.discussion_id} className="glass rounded-xl p-4 mb-3" data-testid={`disc-${d.discussion_id}`}>
                    <button onClick={() => setOpenDisc(isOpen ? null : d.discussion_id)} className="w-full text-left">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-secondary text-muted-foreground">
                          {DISC_CATEGORIES.find(c => c.id === d.category)?.label || 'Общее'}
                        </span>
                        <span className="text-[10px] text-muted-foreground font-mono">{d.reply_count} ответов</span>
                      </div>
                      <h4 className="font-semibold text-foreground text-sm">{d.title}</h4>
                      <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{d.content}</p>
                      <p className="text-[10px] text-muted-foreground mt-2">{d.author_name} — {new Date(d.created_at).toLocaleDateString('ru-RU')}</p>
                    </button>
                    {isOpen && (
                      <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} className="mt-3 pt-3 border-t border-border/50">
                        {(d.replies || []).map(r => (
                          <div key={r.reply_id} className="ml-4 mb-2 p-2 bg-secondary/30 rounded-lg">
                            <p className="text-xs text-foreground">{r.text}</p>
                            <p className="text-[10px] text-muted-foreground mt-1">{r.author_name} — {new Date(r.created_at).toLocaleDateString('ru-RU')}</p>
                          </div>
                        ))}
                        {isMember && (
                          <div className="flex gap-2 mt-2">
                            <input type="text" value={replyText[d.discussion_id] || ''}
                              onChange={e => setReplyText(p => ({ ...p, [d.discussion_id]: e.target.value }))}
                              onKeyDown={e => e.key === 'Enter' && handleReply(d.discussion_id)}
                              placeholder="Ответить..." className="flex-1 bg-secondary/50 rounded-lg h-9 px-3 text-xs outline-none" />
                            <button onClick={() => handleReply(d.discussion_id)} className="p-2 bg-primary text-primary-foreground rounded-lg">
                              <Send className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        )}
                      </motion.div>
                    )}
                  </div>
                );
              })}
            </>
          )}

          {tab === 'votes' && (
            <>
              {isMember && (myRole === 'chairman' || myRole === 'representative') && (
                <button onClick={() => setShowNewVote(true)} data-testid="new-vote-btn"
                  className="w-full glass rounded-xl p-4 mb-4 text-left flex items-center gap-3 hover:border-primary/30 transition-all">
                  <Vote className="w-5 h-5 text-primary" />
                  <span className="text-sm text-muted-foreground">Создать голосование...</span>
                </button>
              )}
              {votes.length === 0 && <p className="text-center text-muted-foreground text-sm py-6">Голосований пока нет</p>}
              {votes.map(v => {
                const hasVoted = v.options?.some(o => o.voters?.includes(user?.user_id));
                return (
                  <div key={v.vote_id} className="glass rounded-xl p-5 mb-3" data-testid={`vote-${v.vote_id}`}>
                    <h4 className="font-semibold text-foreground mb-1">{v.title}</h4>
                    <p className="text-xs text-muted-foreground mb-3">{v.description}</p>
                    <div className="space-y-2">
                      {(v.options || []).map(opt => {
                        const pct = v.total_votes > 0 ? Math.round((opt.votes / v.total_votes) * 100) : 0;
                        const voted = opt.voters?.includes(user?.user_id);
                        return (
                          <button key={opt.option_id} onClick={() => !hasVoted && handleCastVote(v.vote_id, opt.option_id)}
                            disabled={hasVoted} data-testid={`vote-opt-${opt.option_id}`}
                            className={`w-full text-left p-3 rounded-lg relative overflow-hidden transition-all ${hasVoted ? '' : 'hover:bg-primary/10 cursor-pointer'} ${voted ? 'ring-2 ring-primary/50' : 'bg-secondary/30'}`}>
                            {hasVoted && <div className="absolute inset-y-0 left-0 bg-primary/15 transition-all" style={{ width: `${pct}%` }} />}
                            <div className="relative flex items-center justify-between">
                              <span className="text-sm text-foreground">{opt.text}</span>
                              {hasVoted && <span className="text-xs font-mono text-primary font-bold">{pct}%</span>}
                            </div>
                          </button>
                        );
                      })}
                    </div>
                    <p className="text-[10px] text-muted-foreground mt-2">{v.total_votes} голосов — {v.author_name}</p>
                  </div>
                );
              })}
            </>
          )}

          {tab === 'news' && <NewsTab council={selected} user={user} />}
          {tab === 'nominations' && <NominationsTab council={selected} user={user} onRefresh={refreshCouncil} />}
          {tab === 'escalation' && <EscalationTab council={selected} user={user} />}

          {/* New Discussion Modal */}
          <AnimatePresence>
            {showNewDisc && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowNewDisc(false)}>
                <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
                  onClick={e => e.stopPropagation()} className="glass rounded-2xl p-6 w-full max-w-lg">
                  <h2 className="text-lg font-bold mb-4">Новое обсуждение</h2>
                  <div className="space-y-3">
                    <select value={discForm.category} onChange={e => setDiscForm(p => ({ ...p, category: e.target.value }))}
                      className="w-full bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none">
                      {DISC_CATEGORIES.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
                    </select>
                    <input type="text" value={discForm.title} onChange={e => setDiscForm(p => ({ ...p, title: e.target.value }))}
                      placeholder="Тема (мин. 5)" className="w-full bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" />
                    <textarea value={discForm.content} onChange={e => setDiscForm(p => ({ ...p, content: e.target.value }))}
                      placeholder="Содержание (мин. 20)..." rows={4} className="w-full bg-secondary/50 rounded-xl p-3 text-sm text-foreground outline-none resize-none" />
                    <button onClick={handleNewDisc} disabled={submitting || discForm.title.length < 5 || discForm.content.length < 20}
                      className="w-full bg-primary text-primary-foreground py-3 rounded-xl font-medium disabled:opacity-50">
                      {submitting ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Опубликовать'}
                    </button>
                  </div>
                </motion.div>
              </div>
            )}
          </AnimatePresence>

          {/* New Vote Modal */}
          <AnimatePresence>
            {showNewVote && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowNewVote(false)}>
                <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
                  onClick={e => e.stopPropagation()} className="glass rounded-2xl p-6 w-full max-w-lg">
                  <h2 className="text-lg font-bold mb-4">Новое голосование</h2>
                  <div className="space-y-3">
                    <input type="text" value={voteForm.title} onChange={e => setVoteForm(p => ({ ...p, title: e.target.value }))}
                      placeholder="Вопрос" className="w-full bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" />
                    <textarea value={voteForm.description} onChange={e => setVoteForm(p => ({ ...p, description: e.target.value }))}
                      placeholder="Описание..." rows={2} className="w-full bg-secondary/50 rounded-xl p-3 text-sm text-foreground outline-none resize-none" />
                    {voteForm.options.map((opt, i) => (
                      <div key={i} className="flex gap-2">
                        <input type="text" value={opt} onChange={e => { const o = [...voteForm.options]; o[i] = e.target.value; setVoteForm(p => ({ ...p, options: o })); }}
                          placeholder={`Вариант ${i + 1}`} className="flex-1 bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" />
                        {i > 1 && <button onClick={() => setVoteForm(p => ({ ...p, options: p.options.filter((_, j) => j !== i) }))} className="text-muted-foreground"><X className="w-4 h-4" /></button>}
                      </div>
                    ))}
                    {voteForm.options.length < 10 && (
                      <button onClick={() => setVoteForm(p => ({ ...p, options: [...p.options, ''] }))} className="text-xs text-primary">+ Добавить вариант</button>
                    )}
                    <button onClick={handleNewVote} disabled={submitting} className="w-full bg-primary text-primary-foreground py-3 rounded-xl font-medium disabled:opacity-50">
                      {submitting ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Создать голосование'}
                    </button>
                  </div>
                </motion.div>
              </div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    );
  }

  // ======================== LIST VIEW ========================
  return (
    <div className="max-w-3xl mx-auto" data-testid="councils-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight" style={{ fontFamily: 'Manrope' }}>Народные Советы</h1>
            <p className="text-muted-foreground text-sm mt-1">Система гражданского самоуправления</p>
          </div>
          <button onClick={() => setShowCreate(true)} data-testid="create-council-btn"
            className="bg-primary text-primary-foreground px-4 py-2.5 rounded-xl text-sm font-medium flex items-center gap-2">
            <Plus className="w-4 h-4" /> Создать двор
          </button>
        </div>

        {/* Info banner */}
        <div className="glass rounded-xl p-4 mb-4 border border-primary/20 bg-primary/5">
          <p className="text-xs text-muted-foreground leading-relaxed">
            <strong className="text-foreground">Как это работает:</strong> Создайте дворовый совет для вашего дома. Когда 80% верифицированных жителей вступят, совет считается сформированным. Затем председатели/представители голосуют за создание районного совета, и далее по ступеням.
          </p>
        </div>

        {/* Level filters */}
        <div className="flex gap-2 overflow-x-auto pb-2 mb-4 scrollbar-hide">
          <button onClick={() => setFilterLevel('')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap shrink-0 ${!filterLevel ? 'bg-primary text-primary-foreground' : 'glass text-muted-foreground'}`}>
            Все
          </button>
          {Object.entries(LEVEL_CONFIG).map(([key, cfg]) => (
            <button key={key} onClick={() => setFilterLevel(key)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap shrink-0 ${filterLevel === key ? 'text-white' : 'glass text-muted-foreground'}`}
              style={filterLevel === key ? { backgroundColor: cfg.color } : {}}>
              {cfg.name}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
        ) : councils.length === 0 ? (
          <div className="glass rounded-xl p-8 text-center">
            <Users className="w-12 h-12 text-muted-foreground/20 mx-auto mb-3" />
            <p className="text-muted-foreground">Советов пока нет. Создайте первый дворовый совет!</p>
          </div>
        ) : (
          <div className="space-y-2">
            {councils.map(c => {
              const lvl = LEVEL_CONFIG[c.level] || LEVEL_CONFIG.yard;
              const isPending = !c.confirmed;
              return (
                <button key={c.council_id} onClick={() => openCouncil(c)}
                  className="w-full glass rounded-xl p-4 text-left hover:border-primary/30 transition-all"
                  data-testid={`council-${c.council_id}`}>
                  <div className="flex items-center gap-4">
                    <div className="w-11 h-11 rounded-xl flex items-center justify-center shrink-0" style={{ backgroundColor: lvl.color + '20' }}>
                      <Users className="w-5 h-5" style={{ color: lvl.color }} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-0.5 flex-wrap">
                        <span className="text-[10px] px-1.5 py-0.5 rounded text-white" style={{ backgroundColor: lvl.color }}>{lvl.name}</span>
                        {isPending && <span className="text-[10px] px-1.5 py-0.5 rounded bg-yellow-500/20 text-yellow-400">Ожидание</span>}
                        {!isPending && <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/20 text-green-400">Активен</span>}
                      </div>
                      <p className="text-sm font-semibold text-foreground truncate">{c.name}</p>
                      {c.address && <p className="text-[10px] text-muted-foreground mt-0.5">{c.address}</p>}
                      <div className="flex items-center gap-3 mt-1 text-[10px] text-muted-foreground">
                        <span>{c.member_count} уч.</span>
                        <span>{c.discussion_count || 0} обсужд.</span>
                      </div>
                      {isPending && (
                        <div className="mt-1.5">
                          <div className="w-full bg-secondary/50 rounded-full h-1.5 overflow-hidden">
                            <div className="h-full rounded-full bg-yellow-500 transition-all" style={{ width: `${Math.min(((c.confirmations?.length || 0) / (c.confirmations_needed || 10)) * 100, 100)}%` }} />
                          </div>
                          <span className="text-[9px] text-yellow-400">{c.confirmations?.length || 0}/{c.confirmations_needed || 10} подтверждений</span>
                        </div>
                      )}
                    </div>
                    <ChevronRight className="w-4 h-4 text-muted-foreground shrink-0" />
                  </div>
                </button>
              );
            })}
          </div>
        )}

        {/* Create Yard Council Modal */}
        <AnimatePresence>
          {showCreate && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowCreate(false)}>
              <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
                onClick={e => e.stopPropagation()} className="glass rounded-2xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto" data-testid="create-council-modal">
                <h2 className="text-lg font-bold mb-1">Создать дворовый совет</h2>
                <p className="text-xs text-muted-foreground mb-4">Один дом — один совет. Для активации нужно 10 подтверждений.</p>
                <div className="space-y-3">
                  <input type="text" value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))}
                    placeholder="Название совета (мин. 3 символа)" className="w-full bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" data-testid="council-name" />
                  <textarea value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))}
                    placeholder="Описание (мин. 10 символов)..." rows={3}
                    className="w-full bg-secondary/50 rounded-xl p-3 text-sm text-foreground outline-none resize-none" data-testid="council-description" />

                  <div className="border border-border/50 rounded-xl p-4 bg-secondary/10">
                    <h3 className="text-xs font-medium text-foreground mb-2 flex items-center gap-1.5"><Home className="w-3.5 h-3.5 text-primary" /> Адрес дома</h3>
                    <div className="grid grid-cols-2 gap-2">
                      <input type="text" value={form.street} onChange={e => setForm(p => ({ ...p, street: e.target.value }))}
                        placeholder="Улица *" className="bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" data-testid="council-street" />
                      <input type="text" value={form.house_number} onChange={e => setForm(p => ({ ...p, house_number: e.target.value }))}
                        placeholder="Номер дома *" className="bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" data-testid="council-house" />
                      <input type="text" value={form.district} onChange={e => setForm(p => ({ ...p, district: e.target.value }))}
                        placeholder="Район" className="bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" data-testid="council-district" />
                      <input type="text" value={form.city} onChange={e => setForm(p => ({ ...p, city: e.target.value }))}
                        placeholder="Город" className="bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" data-testid="council-city" />
                    </div>
                  </div>

                  {/* Legal Consent */}
                  <div className="bg-secondary/30 rounded-xl p-4 border border-border/50" data-testid="legal-consent-block">
                    <div className="flex items-start gap-3">
                      <FileText className="w-5 h-5 text-primary mt-0.5 shrink-0" />
                      <p className="text-[10px] text-muted-foreground leading-relaxed">
                        Создавая совет, вы подтверждаете, что действуете в рамках законодательства Кыргызской Республики (ОсОО, ПВТ, г. Бишкек).
                        Платформа не несёт ответственности за действия участников советов.
                      </p>
                    </div>
                    <label className="flex items-center gap-2 mt-3 cursor-pointer">
                      <input type="checkbox" checked={form.legal_consent}
                        onChange={e => setForm(p => ({ ...p, legal_consent: e.target.checked }))}
                        className="w-4 h-4 rounded border-border accent-primary" data-testid="legal-consent-checkbox" />
                      <span className="text-xs text-foreground">Принимаю условия</span>
                    </label>
                  </div>

                  <button onClick={handleCreate}
                    disabled={submitting || form.name.length < 3 || form.description.length < 10 || !form.street || !form.house_number || !form.legal_consent}
                    data-testid="submit-council"
                    className="w-full bg-primary text-primary-foreground py-3 rounded-xl font-medium disabled:opacity-50 flex items-center justify-center gap-2">
                    {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Users className="w-4 h-4" /> Создать дворовый совет</>}
                  </button>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
