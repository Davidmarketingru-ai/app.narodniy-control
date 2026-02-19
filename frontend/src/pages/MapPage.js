import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { motion } from 'framer-motion';
import { MapPin, Star, Search, X } from 'lucide-react';
import { organizationsApi } from '../lib/api';
import { Link } from 'react-router-dom';

const categoryColors = {
  shop: '#3b82f6',
  cafe: '#eab308',
  restaurant: '#ef4444',
  pharmacy: '#10b981',
  entertainment: '#8b5cf6',
  other: '#6b7280',
};

const categoryLabels = {
  shop: 'Магазин',
  cafe: 'Кафе',
  restaurant: 'Ресторан',
  pharmacy: 'Аптека',
  entertainment: 'Развлечения',
  other: 'Другое',
};

function createMarkerIcon(category) {
  const color = categoryColors[category] || categoryColors.other;
  return L.divIcon({
    className: '',
    html: `<div style="
      width: 32px; height: 32px; border-radius: 50%; 
      background: ${color}; border: 3px solid white;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      display: flex; align-items: center; justify-content: center;
    ">
      <div style="width: 8px; height: 8px; border-radius: 50%; background: white;"></div>
    </div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
}

export default function MapPage() {
  const [orgs, setOrgs] = useState([]);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    organizationsApi.list().then(setOrgs).catch(console.error).finally(() => setLoading(false));
  }, []);

  const filtered = orgs.filter(o => {
    const matchSearch = !search || o.name.toLowerCase().includes(search.toLowerCase()) || o.address.toLowerCase().includes(search.toLowerCase());
    const matchCategory = !selectedCategory || o.category === selectedCategory;
    return matchSearch && matchCategory;
  });

  const categories = Object.keys(categoryLabels);

  return (
    <div className="h-[calc(100vh-80px)] md:h-[calc(100vh-32px)] flex flex-col" data-testid="map-page">
      {/* Search & Filters */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-4 space-y-3">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Поиск заведений..."
            data-testid="map-search-input"
            className="w-full bg-secondary/50 border border-transparent focus:border-primary rounded-xl h-12 pl-11 pr-4 text-foreground placeholder:text-muted-foreground outline-none transition-colors"
          />
          {search && (
            <button onClick={() => setSearch('')} className="absolute right-4 top-1/2 -translate-y-1/2">
              <X className="w-4 h-4 text-muted-foreground" />
            </button>
          )}
        </div>
        <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all ${!selectedCategory ? 'bg-primary text-primary-foreground' : 'glass text-muted-foreground hover:text-foreground'}`}
          >
            Все
          </button>
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(selectedCategory === cat ? null : cat)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all ${selectedCategory === cat ? 'text-white' : 'glass text-muted-foreground hover:text-foreground'}`}
              style={selectedCategory === cat ? { background: categoryColors[cat] } : {}}
            >
              {categoryLabels[cat]}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Map */}
      <div className="flex-1 rounded-xl overflow-hidden border border-border/50 relative">
        <MapContainer
          center={[43.023, 44.682]}
          zoom={14}
          className="w-full h-full"
          zoomControl={false}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; OpenStreetMap'
          />
          {filtered.map(org => (
            <Marker
              key={org.org_id}
              position={[org.latitude, org.longitude]}
              icon={createMarkerIcon(org.category)}
            >
              <Popup className="custom-popup">
                <div className="p-1 min-w-[180px]">
                  <h3 className="font-semibold text-sm mb-1">{org.name}</h3>
                  <p className="text-xs text-gray-600 mb-1">{org.address}</p>
                  <div className="flex items-center gap-1 mb-2">
                    <Star className="w-3 h-3 text-yellow-500 fill-yellow-500" />
                    <span className="text-xs font-medium">{org.average_rating}</span>
                    <span className="text-xs text-gray-500">({org.review_count} отзывов)</span>
                  </div>
                  <span className="inline-block text-xs px-2 py-0.5 rounded-full text-white" style={{ background: categoryColors[org.category] || '#6b7280' }}>
                    {categoryLabels[org.category] || 'Другое'}
                  </span>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>

        {/* Floating legend */}
        <div className="absolute bottom-4 left-4 glass rounded-lg p-3 z-[1000]">
          <p className="text-xs font-medium text-foreground mb-2">
            <MapPin className="w-3 h-3 inline mr-1" />{filtered.length} заведений
          </p>
        </div>
      </div>

      {/* Organization list */}
      <div className="mt-4 space-y-2 max-h-40 overflow-y-auto">
        {filtered.slice(0, 4).map(org => (
          <div key={org.org_id} className="glass rounded-lg p-3 flex items-center justify-between" data-testid={`org-list-${org.org_id}`}>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full" style={{ background: categoryColors[org.category] || '#6b7280' }} />
              <div>
                <p className="text-sm font-medium text-foreground">{org.name}</p>
                <p className="text-xs text-muted-foreground">{org.address}</p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
              <span className="text-xs font-mono text-foreground">{org.average_rating}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
