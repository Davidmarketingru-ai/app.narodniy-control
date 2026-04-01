import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  HelpCircle, Plus, MessageSquare, Clock, CheckCircle2,
  Loader2, Send, ChevronDown, ChevronRight, AlertTriangle,
  Bug, Lightbulb, ShieldAlert, X, ArrowLeft
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import api from '../lib/api';

const CATEGORIES = [
  { id: 'question', label: 'Вопрос', icon: HelpCircle, color: '#3b82f6' },
  { id: 'bug', label: 'Ошибка', icon: Bug, color: '#ef4444' },
  { id: 'complaint', label: 'Жалоба', icon: AlertTriangle, color: '#f97316' },
  { id: 'suggestion', label: 'Предложение', icon: Lightbulb, color: '#10b981' },
  { id: 'rights_violation', label: 'Нарушение прав', icon: ShieldAlert, color: '#dc2626' },
  { id: 'other', label: 'Другое', icon: MessageSquare, color: '#6b7280' },
];

const STATUS_CONFIG = {
  open: { label: 'Открыт', color: '#3b82f6', bg: 'bg-blue-500/10' },
  in_progress: { label: 'В работе', color: '#eab308', bg: 'bg-yellow-500/10' },
  resolved: { label: 'Решён', color: '#10b981', bg: 'bg-emerald-500/10' },
  closed: { label: 'Закрыт', color: '#6b7280', bg: 'bg-gray-500/10' },
};

function FAQSection({ faq }) {
  const [openIdx, setOpenIdx] = useState(null);
  return (
    <div className="space-y-2" data-testid="faq-section">
      {faq.map((item, i) => (
        <div key={i} className="glass rounded-xl overflow-hidden">
          <button onClick={() => setOpenIdx(openIdx === i ? null : i)}
            className="w-full flex items-center justify-between p-4 text-left" data-testid={`faq-item-${i}`}>
            <span className="text-sm font-medium text-foreground pr-4">{item.question}</span>
            <ChevronDown className={`w-4 h-4 text-muted-foreground shrink-0 transition-transform ${openIdx === i ? 'rotate-180' : ''}`} />
          </button>
          <AnimatePresence>
            {openIdx === i && (
              <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }} className="overflow-hidden">
                <p className="px-4 pb-4 text-sm text-muted-foreground">{item.answer}</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      ))}
    </div>
  );
}

export default function SupportPage() {
  const { user } = useAuth();
  const [tab, setTab] = useState('faq');
  const [faq, setFaq] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [newSubject, setNewSubject] = useState('');
  const [newMessage, setNewMessage] = useState('');
  const [newCategory, setNewCategory] = useState('question');
  const [creating, setCreating] = useState(false);
  const [replyText, setReplyText] = useState('');
  const [replying, setReplying] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get('/support/faq').then(r => r.data).catch(() => []),
      api.get('/support/tickets').then(r => r.data).catch(() => []),
    ]).then(([f, t]) => { setFaq(f); setTickets(t); }).finally(() => setLoading(false));
  }, []);

  const handleCreate = async () => {
    if (!newSubject.trim() || !newMessage.trim()) return;
    setCreating(true);
    try {
      const res = await api.post('/support/tickets', { subject: newSubject, message: newMessage, category: newCategory });
      setTickets(prev => [res.data, ...prev]);
      setShowCreate(false); setNewSubject(''); setNewMessage(''); setNewCategory('question');
      setTab('tickets');
    } catch {}
    finally { setCreating(false); }
  };

  const openTicket = async (ticket) => {
    try {
      const res = await api.get(`/support/tickets/${ticket.ticket_id}`);
      setSelectedTicket(res.data);
    } catch { setSelectedTicket(ticket); }
  };

  const handleReply = async () => {
    if (!replyText.trim() || !selectedTicket) return;
    setReplying(true);
    try {
      const res = await api.post(`/support/tickets/${selectedTicket.ticket_id}/reply`, { text: replyText });
      setSelectedTicket(res.data);
      setReplyText('');
      setTickets(prev => prev.map(t => t.ticket_id === selectedTicket.ticket_id ? res.data : t));
    } catch {}
    finally { setReplying(false); }
  };

  const handleClose = async (ticketId) => {
    try {
      await api.put(`/support/tickets/${ticketId}/status`, { status: 'closed' });
      setTickets(prev => prev.map(t => t.ticket_id === ticketId ? { ...t, status: 'closed' } : t));
      if (selectedTicket?.ticket_id === ticketId) setSelectedTicket(prev => ({ ...prev, status: 'closed' }));
    } catch {}
  };

  if (selectedTicket) {
    const cfg = STATUS_CONFIG[selectedTicket.status] || STATUS_CONFIG.open;
    const cat = CATEGORIES.find(c => c.id === selectedTicket.category) || CATEGORIES[5];
    return (
      <div className="max-w-3xl mx-auto" data-testid="ticket-detail">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <button onClick={() => setSelectedTicket(null)} className="flex items-center gap-2 text-sm text-muted-foreground mb-4 hover:text-foreground transition-colors">
            <ArrowLeft className="w-4 h-4" /> Назад к обращениям
          </button>
          <div className="glass rounded-xl p-6 mb-4">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h2 className="text-xl font-bold text-foreground">{selectedTicket.subject}</h2>
                <div className="flex items-center gap-3 mt-2">
                  <span className="text-xs px-2 py-0.5 rounded-full text-white" style={{ backgroundColor: cat.color }}>{cat.label}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${cfg.bg}`} style={{ color: cfg.color }}>{cfg.label}</span>
                  <span className="text-xs text-muted-foreground font-mono">#{selectedTicket.ticket_id.slice(-6)}</span>
                </div>
              </div>
              {selectedTicket.status !== 'closed' && (
                <button onClick={() => handleClose(selectedTicket.ticket_id)} className="text-xs text-muted-foreground hover:text-foreground px-3 py-1.5 glass rounded-lg" data-testid="close-ticket-btn">
                  Закрыть
                </button>
              )}
            </div>
          </div>

          <div className="space-y-3 mb-4">
            {(selectedTicket.messages || []).map((msg) => (
              <motion.div key={msg.message_id} initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }}
                className={`rounded-xl p-4 ${msg.sender === 'support' ? 'bg-primary/10 border border-primary/20 ml-4' : 'glass mr-4'}`}>
                <div className="flex items-center gap-2 mb-2">
                  <span className={`text-xs font-medium ${msg.sender === 'support' ? 'text-primary' : 'text-foreground'}`}>
                    {msg.sender_name}
                  </span>
                  {msg.sender === 'support' && <span className="text-[10px] bg-primary/20 text-primary px-1.5 py-0.5 rounded">Поддержка</span>}
                  <span className="text-[10px] text-muted-foreground font-mono">{new Date(msg.created_at).toLocaleString('ru-RU')}</span>
                </div>
                <p className="text-sm text-foreground whitespace-pre-wrap">{msg.text}</p>
              </motion.div>
            ))}
          </div>

          {selectedTicket.status !== 'closed' && (
            <div className="flex gap-2">
              <input type="text" value={replyText} onChange={e => setReplyText(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleReply()}
                placeholder="Написать ответ..." data-testid="ticket-reply-input"
                className="flex-1 bg-secondary/50 border border-transparent focus:border-primary rounded-xl h-11 px-4 text-sm text-foreground placeholder:text-muted-foreground outline-none" />
              <button onClick={handleReply} disabled={!replyText.trim() || replying} data-testid="ticket-reply-btn"
                className="bg-primary text-primary-foreground p-3 rounded-xl disabled:opacity-50">
                {replying ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </button>
            </div>
          )}
        </motion.div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto" data-testid="support-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight" style={{ fontFamily: 'Manrope' }}>Техподдержка</h1>
            <p className="text-muted-foreground text-sm mt-1">Ответы на вопросы и система обращений</p>
          </div>
          <button onClick={() => setShowCreate(true)} data-testid="create-ticket-btn"
            className="bg-primary text-primary-foreground px-4 py-2.5 rounded-xl text-sm font-medium flex items-center gap-2 hover:bg-primary/90 transition-all">
            <Plus className="w-4 h-4" /> Обращение
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 glass rounded-xl p-1 mb-6">
          {[{ id: 'faq', label: 'Частые вопросы' }, { id: 'tickets', label: `Мои обращения (${tickets.length})` }].map(t => (
            <button key={t.id} onClick={() => setTab(t.id)} data-testid={`tab-${t.id}`}
              className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-all ${tab === t.id ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'}`}>
              {t.label}
            </button>
          ))}
        </div>

        {/* Create Ticket Modal */}
        <AnimatePresence>
          {showCreate && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowCreate(false)}>
              <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
                onClick={e => e.stopPropagation()} className="glass rounded-2xl p-6 w-full max-w-lg" data-testid="create-ticket-modal">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-bold text-foreground">Новое обращение</h2>
                  <button onClick={() => setShowCreate(false)}><X className="w-5 h-5 text-muted-foreground" /></button>
                </div>
                <div className="space-y-3">
                  <div className="grid grid-cols-3 gap-2">
                    {CATEGORIES.slice(0, 6).map(cat => (
                      <button key={cat.id} onClick={() => setNewCategory(cat.id)} data-testid={`category-${cat.id}`}
                        className={`p-2.5 rounded-xl text-center transition-all text-xs font-medium ${newCategory === cat.id ? 'ring-2 ring-offset-1 ring-offset-background' : 'glass'}`}
                        style={newCategory === cat.id ? { backgroundColor: cat.color + '20', color: cat.color, ringColor: cat.color } : {}}>
                        <cat.icon className="w-4 h-4 mx-auto mb-1" style={{ color: cat.color }} />
                        {cat.label}
                      </button>
                    ))}
                  </div>
                  <input type="text" value={newSubject} onChange={e => setNewSubject(e.target.value)} placeholder="Тема обращения" data-testid="ticket-subject-input"
                    className="w-full bg-secondary/50 border border-transparent focus:border-primary rounded-xl h-11 px-4 text-foreground placeholder:text-muted-foreground outline-none text-sm" />
                  <textarea value={newMessage} onChange={e => setNewMessage(e.target.value)} placeholder="Опишите проблему подробно..." rows={4} data-testid="ticket-message-input"
                    className="w-full bg-secondary/50 border border-transparent focus:border-primary rounded-xl p-3 text-foreground placeholder:text-muted-foreground outline-none resize-none text-sm" />
                  <button onClick={handleCreate} disabled={creating || !newSubject.trim() || !newMessage.trim()} data-testid="submit-ticket-btn"
                    className="w-full bg-primary text-primary-foreground py-3 rounded-xl font-medium disabled:opacity-50 flex items-center justify-center gap-2">
                    {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Send className="w-4 h-4" /> Отправить</>}
                  </button>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>

        {loading ? (
          <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
        ) : tab === 'faq' ? (
          <FAQSection faq={faq} />
        ) : tickets.length === 0 ? (
          <div className="glass rounded-xl p-8 text-center">
            <MessageSquare className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
            <p className="text-muted-foreground">У вас пока нет обращений</p>
          </div>
        ) : (
          <div className="space-y-2">
            {tickets.map((t) => {
              const cfg = STATUS_CONFIG[t.status] || STATUS_CONFIG.open;
              const cat = CATEGORIES.find(c => c.id === t.category) || CATEGORIES[5];
              const CatIcon = cat.icon;
              return (
                <motion.button key={t.ticket_id} onClick={() => openTicket(t)} initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }}
                  className="w-full glass rounded-xl p-4 text-left hover:border-primary/30 transition-all flex items-center gap-4" data-testid={`ticket-${t.ticket_id}`}>
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0" style={{ backgroundColor: cat.color + '20' }}>
                    <CatIcon className="w-5 h-5" style={{ color: cat.color }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">{t.subject}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`text-[10px] px-1.5 py-0.5 rounded ${cfg.bg}`} style={{ color: cfg.color }}>{cfg.label}</span>
                      <span className="text-[10px] text-muted-foreground font-mono">{new Date(t.updated_at).toLocaleDateString('ru-RU')}</span>
                      <span className="text-[10px] text-muted-foreground">{(t.messages || []).length} сообщ.</span>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground shrink-0" />
                </motion.button>
              );
            })}
          </div>
        )}
      </motion.div>
    </div>
  );
}
