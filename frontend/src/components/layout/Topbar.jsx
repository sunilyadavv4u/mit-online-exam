import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Bell, Menu, LogOut, User as UserIcon, Settings } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { notificationsApi } from '../../api/endpoints';
import InstituteBrand from './InstituteBrand';

export default function Topbar({ onToggleSidebar }) {
  const { user, logout } = useAuth();
  const [unread, setUnread] = useState(0);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const tick = () => {
      notificationsApi
        .unreadCount()
        .then((r) => !cancelled && setUnread(r.data.count))
        .catch(() => {});
    };
    tick();
    const interval = setInterval(tick, 30000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white/80 backdrop-blur px-4">
      <div className="flex items-center gap-2 min-w-0">
        <button
          type="button"
          onClick={onToggleSidebar}
          className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 shrink-0"
          aria-label="Toggle sidebar"
        >
          <Menu className="h-5 w-5" />
        </button>
        <div className="hidden sm:block border-l border-slate-200 pl-2">
          <InstituteBrand className="py-1" />
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Link
          to="/notifications"
          className="relative rounded-lg p-2 text-slate-600 hover:bg-slate-100"
        >
          <Bell className="h-5 w-5" />
          {unread > 0 && (
            <span className="absolute right-1 top-1 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-semibold text-white">
              {unread > 9 ? '9+' : unread}
            </span>
          )}
        </Link>

        <div className="relative">
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            className="flex items-center gap-2 rounded-lg px-3 py-1.5 hover:bg-slate-100"
          >
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-700 text-white flex items-center justify-center text-sm font-semibold">
              {(user?.first_name?.[0] || user?.email?.[0] || 'U').toUpperCase()}
            </div>
            <span className="hidden text-sm font-medium text-slate-700 md:inline">
              {user?.full_name || user?.email}
            </span>
          </button>
          {open && (
            <div
              className="absolute right-0 mt-2 w-56 rounded-xl border border-slate-200 bg-white py-2 shadow-lg"
              onMouseLeave={() => setOpen(false)}
            >
              <Link to="/profile" className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-slate-50">
                <UserIcon className="h-4 w-4" /> Profile
              </Link>
              <Link to="/settings" className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-slate-50">
                <Settings className="h-4 w-4" /> Settings
              </Link>
              <button
                onClick={() => logout()}
                className="flex w-full items-center gap-2 px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50"
              >
                <LogOut className="h-4 w-4" /> Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
