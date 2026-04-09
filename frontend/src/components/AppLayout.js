import React, { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Home, Map, PlusCircle, Bell, User, Award, Shield,
  Menu, X, LogOut, Star, ShieldAlert, Newspaper, LayoutGrid, MapPin, ShieldCheck, HelpCircle, CheckSquare,
  Building2, Users, BarChart3
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { notificationsApi } from '../lib/api';

const navItems = [
  { to: '/dashboard', label: 'Главная', icon: Home },
  { to: '/news', label: 'Новости', icon: Newspaper },
  { to: '/councils', label: 'Советы', icon: Users },
  { to: '/stats', label: 'Статистика', icon: BarChart3 },
  { to: '/gov', label: 'Госслужащие', icon: Building2 },
  { to: '/verify', label: 'Проверить', icon: CheckSquare },
  { to: '/problems-map', label: 'Проблемы', icon: MapPin },
  { to: '/map', label: 'Карта', icon: Map },
  { to: '/create', label: 'Отзыв', icon: PlusCircle },
  { to: '/widgets', label: 'Инфо', icon: LayoutGrid },
  { to: '/rewards', label: 'Награды', icon: Award },
  { to: '/verification', label: 'Верификация', icon: ShieldCheck },
  { to: '/support', label: 'Поддержка', icon: HelpCircle },
  { to: '/notifications', label: 'Уведомления', icon: Bell },
  { to: '/profile', label: 'Профиль', icon: User },
];

const adminNavItem = { to: '/admin', label: 'Админ', icon: ShieldAlert };

export default function AppLayout({ children }) {
  const { user } = useAuth();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (user) {
      notificationsApi.list()
        .then(notifs => setUnreadCount(notifs.filter(n => !n.is_read).length))
        .catch(() => {});
    }
  }, [user, location.pathname]);

  return (
    <div className="min-h-screen bg-background flex">
      {/* Desktop Sidebar */}
      <aside className="hidden md:flex flex-col w-64 fixed inset-y-0 left-0 glass border-r border-border/50 z-40" data-testid="sidebar">
        <div className="p-6">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center">
              <Shield className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h2 className="font-bold text-foreground text-sm tracking-tight" style={{ fontFamily: 'Manrope' }}>Народный</h2>
              <h2 className="font-bold text-primary text-sm tracking-tight" style={{ fontFamily: 'Manrope' }}>Контроль</h2>
            </div>
          </div>

          <nav className="space-y-1">
            {[...navItems, ...(user?.role === 'admin' ? [adminNavItem] : [])].map(item => (
              <NavLink
                key={item.to}
                to={item.to}
                data-testid={`nav-${item.to.replace('/', '')}`}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-primary/10 text-primary border border-primary/20'
                      : 'text-muted-foreground hover:text-foreground hover:bg-secondary/50'
                  }`
                }
              >
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
                {item.to === '/notifications' && unreadCount > 0 && (
                  <span className="ml-auto bg-primary text-primary-foreground text-xs font-bold px-2 py-0.5 rounded-full">
                    {unreadCount}
                  </span>
                )}
              </NavLink>
            ))}
          </nav>
        </div>

        {/* User card at bottom */}
        {user && (
          <div className="mt-auto p-6 border-t border-border/50">
            <div className="flex items-center gap-3 mb-3">
              {user.picture ? (
                <img src={user.picture} alt="" className="w-9 h-9 rounded-full object-cover" />
              ) : (
                <div className="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center">
                  <User className="w-4 h-4 text-primary" />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground truncate">{user.name}</p>
                <p className="text-xs text-muted-foreground font-mono">{user.points || 0} баллов</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-[10px] text-muted-foreground/60">
              <NavLink to="/terms" className="hover:text-muted-foreground">Соглашение</NavLink>
              <span>|</span>
              <NavLink to="/privacy" className="hover:text-muted-foreground">Конфиденциальность</NavLink>
            </div>
          </div>
        )}
      </aside>

      {/* Mobile Header */}
      <div className="md:hidden fixed top-0 left-0 right-0 glass border-b border-border/50 z-40 px-4 py-3 flex items-center justify-between" data-testid="mobile-header">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-primary" />
          <span className="font-bold text-sm text-foreground" style={{ fontFamily: 'Manrope' }}>НК</span>
        </div>
        <button onClick={() => setSidebarOpen(true)} data-testid="mobile-menu-btn">
          <Menu className="w-5 h-5 text-foreground" />
        </button>
      </div>

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSidebarOpen(false)}
              className="fixed inset-0 bg-black/50 z-50 md:hidden"
            />
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="fixed right-0 top-0 bottom-0 w-72 glass border-l border-border/50 z-50 p-6 md:hidden"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-primary" />
                  <span className="font-bold text-foreground" style={{ fontFamily: 'Manrope' }}>Меню</span>
                </div>
                <button onClick={() => setSidebarOpen(false)}>
                  <X className="w-5 h-5 text-foreground" />
                </button>
              </div>
              <nav className="space-y-1">
                {[...navItems, ...(user?.role === 'admin' ? [adminNavItem] : [])].map(item => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    onClick={() => setSidebarOpen(false)}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                        isActive
                          ? 'bg-primary/10 text-primary'
                          : 'text-muted-foreground hover:text-foreground'
                      }`
                    }
                  >
                    <item.icon className="w-5 h-5" />
                    <span>{item.label}</span>
                    {item.to === '/notifications' && unreadCount > 0 && (
                      <span className="ml-auto bg-primary text-primary-foreground text-xs font-bold px-2 py-0.5 rounded-full">
                        {unreadCount}
                      </span>
                    )}
                  </NavLink>
                ))}
              </nav>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="flex-1 md:ml-64 min-h-screen pt-16 md:pt-0">
        <div className="max-w-5xl mx-auto p-4 md:p-8">
          {children}
        </div>
      </main>

      {/* Mobile Bottom Nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 glass border-t border-border/50 z-40 flex items-center justify-around px-2 py-2" data-testid="bottom-nav">
        {[navItems[0], navItems[1], navItems[2], navItems[3], navItems[12]].map(item => {
          const isActive = location.pathname === item.to || (item.to === '/dashboard' && location.pathname === '/');
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className="flex flex-col items-center gap-0.5 py-1 px-3 relative"
            >
              <item.icon className={`w-5 h-5 ${isActive ? 'text-primary' : 'text-muted-foreground'} transition-colors`} />
              <span className={`text-[10px] ${isActive ? 'text-primary font-medium' : 'text-muted-foreground'}`}>{item.label}</span>
              {item.to === '/notifications' && unreadCount > 0 && (
                <span className="absolute -top-0.5 right-1 w-4 h-4 bg-destructive text-white text-[9px] font-bold rounded-full flex items-center justify-center">
                  {unreadCount}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>
    </div>
  );
}
