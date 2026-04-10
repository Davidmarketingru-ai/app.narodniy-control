import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, Send, Loader2, MapPin } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import api from '../lib/api';

export default function DistrictChatPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const endRef = useRef(null);
  const district = user?.district;

  const loadMessages = useCallback(async () => {
    try {
      const data = await api.get('/chats/district').then(r => r.data);
      setMessages(data);
    } catch {} finally { setLoading(false); }
  }, []);

  useEffect(() => {
    loadMessages();
    const interval = setInterval(loadMessages, 5000);
    return () => clearInterval(interval);
  }, [loadMessages]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!text.trim() || text.length < 2) return;
    setSending(true);
    try {
      await api.post('/chats/district', { text: text.trim() });
      setText('');
      loadMessages();
    } catch (e) { alert(e.response?.data?.detail || 'Ошибка'); }
    finally { setSending(false); }
  };

  if (!district) {
    return (
      <div className="max-w-3xl mx-auto flex items-center justify-center min-h-[60vh]" data-testid="district-chat-no-district">
        <div className="glass rounded-xl p-8 text-center">
          <MapPin className="w-12 h-12 text-muted-foreground/20 mx-auto mb-3" />
          <h2 className="text-lg font-bold text-foreground mb-1">Укажите район</h2>
          <p className="text-sm text-muted-foreground">Для доступа к районному чату укажите район в профиле</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto flex flex-col h-[calc(100vh-120px)]" data-testid="district-chat-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-4">
        <h1 className="text-2xl font-bold tracking-tight" style={{ fontFamily: 'Manrope' }}>Чат района</h1>
        <p className="text-muted-foreground text-sm flex items-center gap-1"><MapPin className="w-3.5 h-3.5" /> {district}</p>
      </motion.div>

      <div className="flex-1 glass rounded-xl p-4 overflow-y-auto mb-3 space-y-2" data-testid="chat-messages">
        {loading && <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-primary" /></div>}
        {!loading && messages.length === 0 && (
          <div className="text-center text-muted-foreground text-sm py-8">
            <MessageSquare className="w-8 h-8 mx-auto mb-2 text-muted-foreground/20" />
            Нет сообщений. Начните общение!
          </div>
        )}
        {messages.map(m => {
          const isMe = m.user_id === user?.user_id;
          return (
            <div key={m.message_id} className={`flex ${isMe ? 'justify-end' : 'justify-start'}`} data-testid={`msg-${m.message_id}`}>
              <div className={`max-w-[75%] rounded-2xl px-4 py-2.5 ${isMe ? 'bg-primary text-primary-foreground rounded-br-md' : 'bg-secondary/50 text-foreground rounded-bl-md'}`}>
                {!isMe && <p className="text-[10px] font-medium mb-0.5 opacity-70">{m.user_name}</p>}
                <p className="text-sm whitespace-pre-line">{m.text}</p>
                <p className={`text-[9px] mt-1 ${isMe ? 'opacity-60' : 'text-muted-foreground'}`}>
                  {new Date(m.created_at).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          );
        })}
        <div ref={endRef} />
      </div>

      <div className="flex gap-2 pb-20">
        <input type="text" value={text} onChange={e => setText(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
          placeholder="Сообщение..." maxLength={1000}
          className="flex-1 glass rounded-xl h-12 px-4 text-sm text-foreground outline-none" data-testid="chat-input" />
        <button onClick={handleSend} disabled={sending || !text.trim()}
          className="bg-primary text-primary-foreground rounded-xl px-5 h-12 flex items-center justify-center disabled:opacity-50" data-testid="chat-send">
          {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );
}
