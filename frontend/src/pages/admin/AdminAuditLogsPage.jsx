import { useFetch } from '../../hooks/useFetch';
import { auditApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';
import { formatDate } from '../../utils/helpers';

export default function AdminAuditLogsPage() {
  const { data, loading } = useFetch(() => auditApi.list({ page_size: 100 }), []);
  const list = data?.results || [];

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Audit Logs</h1>
        <p className="text-slate-600">Last 100 state-changing API calls.</p>
      </div>

      {loading ? <Spinner /> : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">When</th>
                <th className="px-4 py-3">User</th>
                <th className="px-4 py-3">Method</th>
                <th className="px-4 py-3">Path</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">IP</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono text-xs">
              {list.map((l) => (
                <tr key={l.id} className="hover:bg-slate-50">
                  <td className="px-4 py-2">{formatDate(l.created_at)}</td>
                  <td className="px-4 py-2">{l.user_email || '-'}</td>
                  <td className="px-4 py-2">
                    <span className={`badge ${l.method === 'POST' ? 'badge-primary' : l.method === 'DELETE' ? 'badge-danger' : 'badge-slate'}`}>
                      {l.method}
                    </span>
                  </td>
                  <td className="px-4 py-2">{l.path}</td>
                  <td className="px-4 py-2">{l.status_code}</td>
                  <td className="px-4 py-2">{l.ip_address}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
