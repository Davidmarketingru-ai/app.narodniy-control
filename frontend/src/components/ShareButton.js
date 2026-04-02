import React, { useState } from 'react';
import { Share2, Copy, Check, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export function ShareButton({ title, text, url, className = '' }) {
  const [showPopup, setShowPopup] = useState(false);
  const [copied, setCopied] = useState(false);
  const fullUrl = url || window.location.href;
  const shareText = text || title || '';

  const handleNativeShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({ title, text: shareText, url: fullUrl });
      } catch {}
      return;
    }
    setShowPopup(true);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(fullUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const shareLinks = [
    { name: 'Telegram', url: `https://t.me/share/url?url=${encodeURIComponent(fullUrl)}&text=${encodeURIComponent(shareText)}`, color: '#0088cc' },
    { name: 'VK', url: `https://vk.com/share.php?url=${encodeURIComponent(fullUrl)}&title=${encodeURIComponent(shareText)}`, color: '#4680C2' },
    { name: 'WhatsApp', url: `https://wa.me/?text=${encodeURIComponent(shareText + ' ' + fullUrl)}`, color: '#25D366' },
  ];

  return (
    <>
      <button onClick={handleNativeShare} data-testid="share-btn"
        className={`inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-primary transition-colors ${className}`}>
        <Share2 className="w-3.5 h-3.5" /> Поделиться
      </button>

      <AnimatePresence>
        {showPopup && (
          <div className="fixed inset-0 bg-black/50 flex items-end md:items-center justify-center z-50 p-4" onClick={() => setShowPopup(false)}>
            <motion.div
              initial={{ y: 100, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 100, opacity: 0 }}
              onClick={e => e.stopPropagation()}
              className="glass rounded-2xl p-6 w-full max-w-sm"
              data-testid="share-popup"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-base font-semibold text-foreground">Поделиться</h3>
                <button onClick={() => setShowPopup(false)}><X className="w-4 h-4 text-muted-foreground" /></button>
              </div>

              <div className="flex gap-3 mb-4">
                {shareLinks.map(link => (
                  <a key={link.name} href={link.url} target="_blank" rel="noopener noreferrer"
                    data-testid={`share-${link.name.toLowerCase()}`}
                    className="flex-1 py-3 rounded-xl text-center text-white text-xs font-medium hover:opacity-90 transition-opacity"
                    style={{ backgroundColor: link.color }}>
                    {link.name}
                  </a>
                ))}
              </div>

              <button onClick={handleCopy} data-testid="share-copy-link"
                className="w-full flex items-center justify-center gap-2 py-3 glass rounded-xl text-sm text-foreground hover:bg-secondary/50 transition-all">
                {copied ? <><Check className="w-4 h-4 text-emerald-400" /> Скопировано!</> : <><Copy className="w-4 h-4" /> Копировать ссылку</>}
              </button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}
