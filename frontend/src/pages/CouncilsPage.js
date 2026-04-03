import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users, Plus, X, Loader2, ChevronRight, MessageSquare, Vote,
  Crown, UserPlus, LogOut, Send, ArrowLeft, Filter
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import api from '../lib/api';

const LEVEL_CONFIG = {
  yard: { name: 'Дворовый', color: '#10b981', emoji: '' },
  district: { name: 'Районный', color: '#3b82f6', emoji: '' },
  city: { name: 'Городской', color: '#8b5cf6', emoji: '' },
  republic: { name: 'Республиканский', color: '#f59e0b', emoji: '' },
  country: { name: 'Народный', color: '#ef4444', emoji: '' },
};

const DISC_CATEGORIES = [
  { id: 'general', label: 'Общее' },
  { id: 'problem', label: 'Проблема' },
  { id: 'proposal', label: 'Предложение' },
  { id: 'budget', label: 'Бюджет' },
  { id: 'event', label: 'Мероприятие' },
];

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
  const [form, setForm] = useState({ name: '', level: 'yard', description: '', address: '' });
  const [discForm, setDiscForm] = useState({ title: '', content: '', category: 'general' });
  const [voteForm, setVoteForm] = useState({ title: '', description: '', options: ['', ''] });
  const [submitting, setSubmitting] = useState(false);
  const [replyText, setReplyText] = useState({});
  const [openDisc, setOpenDisc] = useState(null);

  useEffect(() => {
    loadCouncils();
  }, [filterLevel]);

  const loadCouncils = async () => {
    setLoading(true);
    try {
      const params = filterLevel ? { level: filterLevel } : {};
      const res = await api.get('/councils', { params });
      setCouncils(res.data);
    } catch {} finally { setLoading(false); }
  };

  const openCouncil = async (c) => {
    setSelected(c);
    const [d, v] = await Promise.all([
      api.get(`/councils/${c.council_id}/discussions`).then(r => r.data),
      api.get(`/councils/${c.council_id}/votes`).then(r => r.data),
    ]);
    setDiscussions(d);
    setVotes(v);
    setTab('discussions');
  };

  const isMember = selected && selected.members?.some(m => m.user_id === user?.user_id);
  const myRole = selected?.members?.find(m => m.user_id === user?.user_id)?.role;

  const handleCreate = async () => {
    setSubmitting(true);
    try {
      const res = await api.post('/councils', form);
      setCouncils(prev => [res.data, ...prev]);
      setShowCreate(false);
    } catch (e) { alert(e.response?.data?.detail || 'Ошибка'); }
    finally { setSubmitting(false); }
  };

  const handleJoin = async () => {
    try {
      await api.post(`/councils/${selected.council_id}/join`);
      const res = await api.get(`/councils/${selected.council_id}`);
      setSelected(res.data);
    } catch (e) { alert(e.response?.data?.detail || 'Ошибка'); }
  };

  const handleLeave = async () => {
    try {
      await api.post(`/councils/${selected.council_id}/leave`);
      const res = await api.get(`/councils/${selected.council_id}`);
      setSelected(res.data);
    } catch (e) { alert(e.response?.data?.detail || 'Ошибка'); }
  };

  const handleNewDisc = async () => {
    setSubmitting(true);
    try {
      await api.post(`/councils/${selected.council_id}/discussions`, discForm);
      const d = await api.get(`/councils/${selected.council_id}/discussions`).then(r => r.data);
      setDiscussions(d);
      setShowNewDisc(false);
      setDiscForm({ title: '', content: '', category: 'general' });
    } catch (e) { alert(e.response?.data?.detail || 'Ошибка'); }
    finally { setSubmitting(false); }
  };

  const handleReply = async (discId) => {
    const text = replyText[discId]?.trim();
    if (!text || text.length < 5) return;
    try {
      await api.post(`/councils/${selected.council_id}/discussions/${discId}/reply`, { text });
      const d = await api.get(`/councils/${selected.council_id}/discussions`).then(r => r.data);
      setDiscussions(d);
      setReplyText(prev => ({ ...prev, [discId]: '' }));
    } catch {}
  };

  const handleNewVote = async () => {
    const opts = voteForm.options.filter(o => o.trim());
    if (opts.length < 2) return;
    setSubmitting(true);
    try {
      await api.post(`/councils/${selected.council_id}/votes`, { ...voteForm, options: opts });
      const v = await api.get(`/councils/${selected.council_id}/votes`).then(r => r.data);
      setVotes(v);
      setShowNewVote(false);
      setVoteForm({ title: '', description: '', options: ['', ''] });
    } catch (e) { alert(e.response?.data?.detail || 'Ошибка'); }
    finally { setSubmitting(false); }
  };

  const handleCastVote = async (voteId, optionId) => {
    try {
      await api.post(`/councils/${selected.council_id}/votes/${voteId}/cast`, { option_id: optionId });
      const v = await api.get(`/councils/${selected.council_id}/votes`).then(r => r.data);
      setVotes(v);
    } catch (e) { alert(e.response?.data?.detail || 'Уже проголосовали'); }
  };

  // Detail view
  if (selected) {
    const lvl = LEVEL_CONFIG[selected.level] || LEVEL_CONFIG.yard;
    return (
      <div className="max-w-3xl mx-auto" data-testid="council-detail">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <button onClick={() => setSelected(null)} className="flex items-center gap-2 text-sm text-muted-foreground mb-4 hover:text-foreground">
            <ArrowLeft className="w-4 h-4" /> Все советы
          </button>

          <div className="glass rounded-xl p-6 mb-4">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs px-2 py-0.5 rounded-full text-white" style={{ backgroundColor: lvl.color }}>{lvl.name}</span>
                </div>
                <h2 className="text-xl font-bold text-foreground">{selected.name}</h2>
                <p className="text-sm text-muted-foreground mt-1">{selected.description}</p>
                <p className="text-xs text-muted-foreground mt-2 font-mono">{selected.member_count} участников</p>
              </div>
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

          {/* Members */}
          <div className="glass rounded-xl p-4 mb-4">
            <h3 className="text-sm font-medium text-muted-foreground mb-2">Участники ({selected.members?.length || 0})</h3>
            <div className="flex flex-wrap gap-2">
              {(selected.members || []).slice(0, 20).map(m => (
                <div key={m.user_id} className="flex items-center gap-1.5 bg-secondary/50 px-2.5 py-1 rounded-lg">
                  <span className="text-xs text-foreground">{m.name || 'Участник'}</span>
                  {m.role === 'chairman' && <Crown className="w-3 h-3 text-yellow-400" />}
                </div>
              ))}
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-1 glass rounded-xl p-1 mb-4">
            {[
              { id: 'discussions', label: `Обсуждения (${discussions.length})` },
              { id: 'votes', label: `Голосования (${votes.length})` },
            ].map(t => (
              <button key={t.id} onClick={() => setTab(t.id)}
                className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-all ${tab === t.id ? 'bg-primary text-primary-foreground' : 'text-muted-foreground'}`}>
                {t.label}
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
              {isMember && (myRole === 'chairman' || myRole === 'moderator') && (
                <button onClick={() => setShowNewVote(true)} data-testid="new-vote-btn"
                  className="w-full glass rounded-xl p-4 mb-4 text-left flex items-center gap-3 hover:border-primary/30 transition-all">
                  <Vote className="w-5 h-5 text-primary" />
                  <span className="text-sm text-muted-foreground">Создать голосование...</span>
                </button>
              )}
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
                      placeholder="Тема" className="w-full bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" />
                    <textarea value={discForm.content} onChange={e => setDiscForm(p => ({ ...p, content: e.target.value }))}
                      placeholder="Содержание..." rows={4} className="w-full bg-secondary/50 rounded-xl p-3 text-sm text-foreground outline-none resize-none" />
                    <button onClick={handleNewDisc} disabled={submitting} className="w-full bg-primary text-primary-foreground py-3 rounded-xl font-medium disabled:opacity-50">
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
                      placeholder="Вопрос голосования" className="w-full bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" />
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

  // List view
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
            <Plus className="w-4 h-4" /> Создать
          </button>
        </div>

        {/* Level hierarchy */}
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
            <p className="text-muted-foreground">Советов пока нет. Создайте первый!</p>
          </div>
        ) : (
          <div className="space-y-2">
            {councils.map(c => {
              const lvl = LEVEL_CONFIG[c.level] || LEVEL_CONFIG.yard;
              return (
                <button key={c.council_id} onClick={() => openCouncil(c)}
                  className="w-full glass rounded-xl p-4 text-left hover:border-primary/30 transition-all flex items-center gap-4"
                  data-testid={`council-${c.council_id}`}>
                  <div className="w-11 h-11 rounded-xl flex items-center justify-center shrink-0" style={{ backgroundColor: lvl.color + '20' }}>
                    <Users className="w-5 h-5" style={{ color: lvl.color }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="text-[10px] px-1.5 py-0.5 rounded text-white" style={{ backgroundColor: lvl.color }}>{lvl.name}</span>
                    </div>
                    <p className="text-sm font-semibold text-foreground truncate">{c.name}</p>
                    <div className="flex items-center gap-3 mt-1 text-[10px] text-muted-foreground">
                      <span>{c.member_count} уч.</span>
                      <span>{c.discussion_count || 0} обсужд.</span>
                      <span>{c.vote_count || 0} голос.</span>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground shrink-0" />
                </button>
              );
            })}
          </div>
        )}

        {/* Create Council Modal */}
        <AnimatePresence>
          {showCreate && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowCreate(false)}>
              <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
                onClick={e => e.stopPropagation()} className="glass rounded-2xl p-6 w-full max-w-lg" data-testid="create-council-modal">
                <h2 className="text-lg font-bold mb-4">Создать совет</h2>
                <div className="space-y-3">
                  <select value={form.level} onChange={e => setForm(p => ({ ...p, level: e.target.value }))} data-testid="council-level-select"
                    className="w-full bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none">
                    {Object.entries(LEVEL_CONFIG).map(([k, v]) => <option key={k} value={k}>{v.name} совет</option>)}
                  </select>
                  <input type="text" value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))}
                    placeholder="Название совета" className="w-full bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" data-testid="council-name" />
                  <textarea value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))}
                    placeholder="Описание (мин. 10 символов)..." rows={3}
                    className="w-full bg-secondary/50 rounded-xl p-3 text-sm text-foreground outline-none resize-none" data-testid="council-description" />
                  <input type="text" value={form.address} onChange={e => setForm(p => ({ ...p, address: e.target.value }))}
                    placeholder="Адрес (необязательно)" className="w-full bg-secondary/50 rounded-xl h-11 px-4 text-sm text-foreground outline-none" />
                  <button onClick={handleCreate} disabled={submitting || !form.name} data-testid="submit-council"
                    className="w-full bg-primary text-primary-foreground py-3 rounded-xl font-medium disabled:opacity-50 flex items-center justify-center gap-2">
                    {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Users className="w-4 h-4" /> Создать совет</>}
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
