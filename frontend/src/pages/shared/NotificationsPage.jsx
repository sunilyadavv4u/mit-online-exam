import { useFetch } from '../../hooks/useFetch';
import { notificationsApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';
import EmptyState from '../../components/common/EmptyState';
import { Bell, CheckCheck } from 'lucide-react';
import { formatDate } from '../../utils/helpers';
import toast from 'react-hot-toast';

export default function NotificationsPage() {
  const { data, loading, setData } = useFetch(() => notificationsApi.list(), []);
  const list = data?.results || data || [];

  const markAll = async () => {
    await notificationsApi.markAllRead();
    toast.success('All notifications marked as read');
    const r = await notificationsApi.list();
    setData(r.data);
  };

  return (
    <div className="space-y-6 max-w-3xl animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Notifications</h1>
          <p className="text-slate-600">Updates about your exams and results.</p>
        </div>
        <button className="btn-secondary" onClick={markAll}>
          <CheckCheck className="h-4 w-4" /> Mark all read
        </button>
      </div>

      {loading ? <Spinner /> : list.length === 0 ? (
        <EmptyState icon={Bell} title="No notifications" description="You'll see exam reminders and result alerts here." />
      ) : (
        <ul className="space-y-3">
          {list.map((n) => (
            <li key={n.id} className={`card p-4 ${!n.is_read ? 'border-l-4 border-l-primary-500' : ''}`}>
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold text-slate-900">{n.title}</p>
                  <p className="mt-1 text-sm text-slate-600">{n.message}</p>
                  <p className="mt-2 text-xs text-slate-400">{formatDate(n.created_at)}</p>
                </div>
                {!n.is_read && <span className="badge-primary">New</span>}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
