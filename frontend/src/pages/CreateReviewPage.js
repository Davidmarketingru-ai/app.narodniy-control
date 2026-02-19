import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  MapPin, Camera, Star, Send, Loader2, ChevronDown, X, AlertCircle
} from 'lucide-react';
import { reviewsApi, organizationsApi } from '../lib/api';

export default function CreateReviewPage() {
  const navigate = useNavigate();
  const [orgs, setOrgs] = useState([]);
  const [selectedOrg, setSelectedOrg] = useState(null);
  const [showOrgDropdown, setShowOrgDropdown] = useState(false);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [photos, setPhotos] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    organizationsApi.list().then(setOrgs).catch(console.error);
  }, []);

  const handlePhotoAdd = () => {
    if (photos.length >= 3) return;
    const placeholders = [
      'https://images.unsplash.com/photo-1576186726183-9bd8aa9fa6d9?w=400',
      'https://images.unsplash.com/photo-1760463921697-6ab2c0caca20?w=400',
      'https://images.unsplash.com/photo-1709934730506-fba12664d4e4?w=400',
    ];
    setPhotos([...photos, placeholders[photos.length]]);
  };

  const removePhoto = (index) => {
    setPhotos(photos.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!selectedOrg) { setError('Выберите заведение'); return; }
    if (!title.trim()) { setError('Введите заголовок'); return; }
    if (!content.trim()) { setError('Введите описание'); return; }
    if (rating === 0) { setError('Поставьте оценку'); return; }

    setSubmitting(true);
    try {
      const review = await reviewsApi.create({
        org_id: selectedOrg.org_id,
        title,
        content,
        rating,
        photos,
        latitude: selectedOrg.latitude,
        longitude: selectedOrg.longitude,
      });
      navigate(`/reviews/${review.review_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при создании отзыва');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto" data-testid="create-review-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold tracking-tight mb-2" style={{ fontFamily: 'Manrope' }}>
          Создать отзыв
        </h1>
        <p className="text-muted-foreground mb-6">Сообщите о проблеме — другие пользователи проверят</p>

        {error && (
          <div className="flex items-center gap-2 bg-destructive/10 border border-destructive/20 text-destructive rounded-lg p-3 mb-4" data-testid="create-review-error">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span className="text-sm">{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Organization Select */}
          <div>
            <label className="text-sm font-medium text-foreground mb-2 block">Заведение</label>
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowOrgDropdown(!showOrgDropdown)}
                data-testid="org-select-btn"
                className="w-full glass rounded-xl p-4 flex items-center justify-between text-left hover:border-primary/30 transition-all"
              >
                {selectedOrg ? (
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-primary" />
                    <span className="text-foreground">{selectedOrg.name}</span>
                    <span className="text-xs text-muted-foreground">— {selectedOrg.address}</span>
                  </div>
                ) : (
                  <span className="text-muted-foreground">Выберите заведение...</span>
                )}
                <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform ${showOrgDropdown ? 'rotate-180' : ''}`} />
              </button>
              {showOrgDropdown && (
                <div className="absolute top-full left-0 right-0 mt-1 glass rounded-xl overflow-hidden z-50 max-h-60 overflow-y-auto">
                  {orgs.map(org => (
                    <button
                      key={org.org_id}
                      type="button"
                      onClick={() => { setSelectedOrg(org); setShowOrgDropdown(false); }}
                      className="w-full p-3 text-left hover:bg-primary/10 transition-colors flex items-center gap-3"
                    >
                      <MapPin className="w-4 h-4 text-muted-foreground shrink-0" />
                      <div>
                        <p className="text-sm font-medium text-foreground">{org.name}</p>
                        <p className="text-xs text-muted-foreground">{org.address}</p>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Title */}
          <div>
            <label className="text-sm font-medium text-foreground mb-2 block">Заголовок</label>
            <input
              type="text"
              value={title}
              onChange={e => setTitle(e.target.value)}
              placeholder="Например: Просроченная молочная продукция"
              data-testid="review-title-input"
              className="w-full bg-secondary/50 border border-transparent focus:border-primary rounded-xl h-12 px-4 text-foreground placeholder:text-muted-foreground outline-none transition-colors"
            />
          </div>

          {/* Content */}
          <div>
            <label className="text-sm font-medium text-foreground mb-2 block">Описание проблемы</label>
            <textarea
              value={content}
              onChange={e => setContent(e.target.value)}
              placeholder="Подробно опишите, что вы обнаружили..."
              rows={4}
              data-testid="review-content-input"
              className="w-full bg-secondary/50 border border-transparent focus:border-primary rounded-xl p-4 text-foreground placeholder:text-muted-foreground outline-none resize-none transition-colors"
            />
          </div>

          {/* Rating */}
          <div>
            <label className="text-sm font-medium text-foreground mb-2 block">Оценка</label>
            <div className="flex items-center gap-1" data-testid="review-rating">
              {[1,2,3,4,5].map(s => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setRating(s)}
                  onMouseEnter={() => setHoverRating(s)}
                  onMouseLeave={() => setHoverRating(0)}
                  className="p-1 transition-transform hover:scale-110"
                >
                  <Star className={`w-8 h-8 ${s <= (hoverRating || rating) ? 'text-yellow-400 fill-yellow-400' : 'text-muted-foreground/30'} transition-colors`} />
                </button>
              ))}
            </div>
          </div>

          {/* Photos */}
          <div>
            <label className="text-sm font-medium text-foreground mb-2 block">Фотографии ({photos.length}/3)</label>
            <div className="flex flex-wrap gap-3">
              {photos.map((photo, i) => (
                <div key={i} className="relative w-24 h-24 rounded-lg overflow-hidden group">
                  <img src={photo} alt="" className="w-full h-full object-cover" />
                  <button
                    type="button"
                    onClick={() => removePhoto(i)}
                    className="absolute top-1 right-1 w-6 h-6 bg-black/60 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="w-3 h-3 text-white" />
                  </button>
                </div>
              ))}
              {photos.length < 3 && (
                <button
                  type="button"
                  onClick={handlePhotoAdd}
                  data-testid="add-photo-btn"
                  className="w-24 h-24 rounded-lg border-2 border-dashed border-muted-foreground/30 flex flex-col items-center justify-center gap-1 hover:border-primary/50 transition-colors"
                >
                  <Camera className="w-5 h-5 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">Фото</span>
                </button>
              )}
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={submitting}
            data-testid="submit-review-btn"
            className="w-full bg-primary text-primary-foreground font-medium py-4 rounded-xl hover:bg-primary/90 transition-all disabled:opacity-50 flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(59,130,246,0.3)]"
          >
            {submitting ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <Send className="w-5 h-5" />
                Опубликовать отзыв
              </>
            )}
          </button>
        </form>
      </motion.div>
    </div>
  );
}
