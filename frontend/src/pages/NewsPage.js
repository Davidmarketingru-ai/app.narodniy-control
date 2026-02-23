import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  Newspaper, Heart, MessageSquare, Eye, Plus, AlertTriangle,
  Loader2, ChevronDown, Filter, Send, User, X
} from 'lucide-react';
import { newsApi } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

const levelLabels = {
  yard: 'Двор', district: 'Район', village: 'Село', city: 'Город',
  republic: 'Республика', okrug: 'Округ', country: 'Страна', world: 'Мир',
};
const levelColors = {
  yard: '#10b981', district: '#3b82f6', village: '#8b5cf6', city: '#eab308',
  republic: '#f97316', okrug: '#ef4444', country: '#dc2626', world: '#6b7280',
};
const categoryLabels = {
  general: 'Общее', infrastructure: 'Инфраструктура', health: 'Здоровье',
  community: 'Сообщество', economics: 'Экономика', safety: 'Безопасность',
  ecology: 'Экология', education: 'Образование', transport: 'Транспорт',
};

export default function NewsPage() {
  const { user } = useAuth();
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterLevel, setFilterLevel] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newContent, setNewContent] = useState('');
  const [newLevel, setNewLevel] = useState('city');
  const [newCategory, setNewCategory] = useState('general');
  const [newUrgent, setNewUrgent] = useState(false);
  const [creating, setCreating] = useState(false);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState('');

  useEffect(() => {
    setLoading(true);
    newsApi.list({ level: filterLevel || undefined }).then(setArticles).catch(console.error).finally(() => setLoading(false));
  }, [filterLevel]);

  const handleCreate = async () => {
    if (!newTitle.trim() || !newContent.trim()) return;
    setCreating(true);
    try {
      const article = await newsApi.create({ title: newTitle, content: newContent, level: newLevel, category: newCategory, is_urgent: newUrgent });
      setArticles(prev => [article, ...prev]);
      setShowCreate(false); setNewTitle(''); setNewContent('');
    } catch (e) { console.error(e); }
    finally { setCreating(false); }
  };

  const handleLike = async (articleId) => {
    try {
      const res = await newsApi.like(articleId);
      setArticles(prev => prev.map(a => a.article_id === articleId ? { ...a, likes: a.likes + (res.liked ? 1 : -1) } : a));
    } catch {}
  };

  const openComments = async (article) => {
    setSelectedArticle(article);
    try { const c = await newsApi.comments(article.article_id); setComments(c); } catch {}
  };

  const submitComment = async () => {
    if (!commentText.trim() || !selectedArticle) return;
    try {
      await newsApi.addComment(selectedArticle.article_id, commentText);
      const c = await newsApi.comments(selectedArticle.article_id);
      setComments(c);
      setCommentText('');
      setArticles(prev => prev.map(a => a.article_id === selectedArticle.article_id ? { ...a, comments_count: (a.comments_count || 0) + 1 } : a));
    } catch {}
  };

  return (
    <div data-testid="news-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight" style={{ fontFamily: 'Manrope' }}>Новости</h1>
            <p className="text-muted-foreground text-sm mt-1">События вашего города и страны</p>
          </div>
          <button onClick={() => setShowCreate(!showCreate)} data-testid="create-news-btn"
            className="bg-primary text-primary-foreground px-4 py-2.5 rounded-xl text-sm font-medium flex items-center gap-2 hover:bg-primary/90 transition-all">
            <Plus className="w-4 h-4" /> Написать
          </button>
        </div>

        {/* Level Filters */}
        <div className="flex gap-2 overflow-x-auto pb-2 mb-4 scrollbar-hide">
          <button onClick={() => setFilterLevel('')} className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all ${!filterLevel ? 'bg-primary text-primary-foreground' : 'glass text-muted-foreground'}`}>
            Все
          </button>
          {Object.entries(levelLabels).map(([key, label]) => (
            <button key={key} onClick={() => setFilterLevel(filterLevel === key ? '' : key)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all ${filterLevel === key ? 'text-white' : 'glass text-muted-foreground'}`}
              style={filterLevel === key ? { backgroundColor: levelColors[key] } : {}}>
              {label}
            </button>
          ))}
        </div>

        {/* Create News Form */}
        {showCreate && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} className="glass rounded-xl p-5 mb-6 space-y-3">
            <input type="text" value={newTitle} onChange={e => setNewTitle(e.target.value)} placeholder="Заголовок новости..." data-testid="news-title-input"
              className="w-full bg-secondary/50 border border-transparent focus:border-primary rounded-xl h-11 px-4 text-foreground placeholder:text-muted-foreground outline-none text-sm" />
            <textarea value={newContent} onChange={e => setNewContent(e.target.value)} placeholder="Содержание..." rows={3} data-testid="news-content-input"
              className="w-full bg-secondary/50 border border-transparent focus:border-primary rounded-xl p-3 text-foreground placeholder:text-muted-foreground outline-none resize-none text-sm" />
            <div className="flex flex-wrap gap-2">
              <select value={newLevel} onChange={e => setNewLevel(e.target.value)} className="bg-secondary text-foreground text-xs px-3 py-2 rounded-lg border border-border/50 outline-none">
                {Object.entries(levelLabels).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
              <select value={newCategory} onChange={e => setNewCategory(e.target.value)} className="bg-secondary text-foreground text-xs px-3 py-2 rounded-lg border border-border/50 outline-none">
                {Object.entries(categoryLabels).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground cursor-pointer">
                <input type="checkbox" checked={newUrgent} onChange={e => setNewUrgent(e.target.checked)} className="rounded" />
                <AlertTriangle className="w-3 h-3 text-red-400" /> Срочно
              </label>
            </div>
            <button onClick={handleCreate} disabled={creating || !newTitle.trim() || !newContent.trim()} data-testid="submit-news-btn"
              className="bg-primary text-primary-foreground px-6 py-2.5 rounded-xl text-sm font-medium disabled:opacity-50 flex items-center gap-2">
              {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Send className="w-4 h-4" /> Опубликовать</>}
            </button>
          </motion.div>
        )}

        {/* Articles */}
        {loading ? (
          <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="glass rounded-xl p-5 animate-pulse"><div className="h-4 bg-muted rounded w-3/4 mb-2" /><div className="h-3 bg-muted rounded w-full" /></div>)}</div>
        ) : articles.length === 0 ? (
          <div className="glass rounded-xl p-8 text-center"><Newspaper className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" /><p className="text-muted-foreground">Новостей пока нет</p></div>
        ) : (
          <div className="space-y-3">
            {articles.map((a, i) => (
              <motion.div key={a.article_id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}
                className={`glass rounded-xl p-5 ${a.is_urgent ? 'border-l-2 border-l-red-500' : ''}`} data-testid={`news-article-${a.article_id}`}>
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-medium px-2 py-0.5 rounded-full text-white" style={{ backgroundColor: levelColors[a.level] || '#6b7280' }}>
                        {levelLabels[a.level] || a.level}
                      </span>
                      <span className="text-xs text-muted-foreground">{categoryLabels[a.category] || a.category}</span>
                      {a.is_urgent && <span className="text-xs text-red-400 font-medium flex items-center gap-0.5"><AlertTriangle className="w-3 h-3" />Срочно</span>}
                    </div>
                    <h3 className="font-semibold text-foreground">{a.title}</h3>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground line-clamp-3 mb-3">{a.content}</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    <span>{a.user_name || 'Аноним'}</span>
                    <span className="font-mono">{new Date(a.created_at).toLocaleDateString('ru-RU')}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <button onClick={() => handleLike(a.article_id)} className="flex items-center gap-1 text-xs text-muted-foreground hover:text-red-400 transition-colors" data-testid={`like-${a.article_id}`}>
                      <Heart className="w-3.5 h-3.5" /> {a.likes || 0}
                    </button>
                    <button onClick={() => openComments(a)} className="flex items-center gap-1 text-xs text-muted-foreground hover:text-primary transition-colors" data-testid={`comments-${a.article_id}`}>
                      <MessageSquare className="w-3.5 h-3.5" /> {a.comments_count || 0}
                    </button>
                    <span className="flex items-center gap-1 text-xs text-muted-foreground"><Eye className="w-3.5 h-3.5" /> {a.views || 0}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Comments Modal */}
        {selectedArticle && (
          <div className="fixed inset-0 bg-black/50 flex items-end md:items-center justify-center z-50 p-0 md:p-4" onClick={() => setSelectedArticle(null)}>
            <motion.div initial={{ y: 50, opacity: 0 }} animate={{ y: 0, opacity: 1 }} onClick={e => e.stopPropagation()}
              className="glass rounded-t-2xl md:rounded-2xl p-6 w-full max-w-lg max-h-[80vh] flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-foreground">{selectedArticle.title}</h3>
                <button onClick={() => setSelectedArticle(null)}><X className="w-5 h-5 text-muted-foreground" /></button>
              </div>
              <div className="flex-1 overflow-y-auto space-y-3 mb-4">
                {comments.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-4">Комментариев пока нет</p>
                ) : comments.map(c => (
                  <div key={c.comment_id} className="bg-secondary/30 rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-medium text-foreground">{c.user_name || 'Аноним'}</span>
                      <span className="text-[10px] text-muted-foreground font-mono">{new Date(c.created_at).toLocaleString('ru-RU')}</span>
                    </div>
                    <p className="text-sm text-foreground">{c.text}</p>
                  </div>
                ))}
              </div>
              <div className="flex gap-2">
                <input type="text" value={commentText} onChange={e => setCommentText(e.target.value)} placeholder="Комментарий..." data-testid="comment-input"
                  onKeyDown={e => e.key === 'Enter' && submitComment()}
                  className="flex-1 bg-secondary/50 border border-transparent focus:border-primary rounded-xl h-10 px-4 text-sm text-foreground placeholder:text-muted-foreground outline-none" />
                <button onClick={submitComment} disabled={!commentText.trim()} data-testid="submit-comment-btn"
                  className="bg-primary text-primary-foreground p-2.5 rounded-xl disabled:opacity-50"><Send className="w-4 h-4" /></button>
              </div>
            </motion.div>
          </div>
        )}
      </motion.div>
    </div>
  );
}
