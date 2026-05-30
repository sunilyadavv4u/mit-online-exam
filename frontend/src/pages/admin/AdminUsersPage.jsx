import { useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search } from 'lucide-react';
import toast from 'react-hot-toast';
import { useFetch } from '../../hooks/useFetch';
import { usersApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';

export default function AdminUsersPage() {
  const [params, setParams] = useSearchParams();
  const q = params.get('search') || '';
  const role = params.get('role') || '';
  const isActive = params.get('is_active') || '';

  const setQuery = (key, value) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    setParams(next);
  };

  const apiParams = useMemo(() => {
    const p = { page_size: 50 };
    if (q) p.search = q;
    if (role) p.role = role;
    if (isActive) p.is_active = isActive;
    return p;
  }, [q, role, isActive]);

  const { data, loading, setData } = useFetch(
    () => usersApi.list(apiParams),
    [q, role, isActive]
  );
  const list = data?.results || [];

  const toggleActive = async (u) => {
    try {
      const r = await usersApi.update(u.id, { is_active: !u.is_active });
      setData({ ...data, results: list.map((x) => (x.id === u.id ? r.data : x)) });
      toast.success('Updated');
    } catch {
      toast.error('Could not update');
    }
  };

  const changeRole = async (u, newRole) => {
    try {
      const r = await usersApi.update(u.id, { role: newRole });
      setData({ ...data, results: list.map((x) => (x.id === u.id ? r.data : x)) });
      toast.success('Role updated');
    } catch {
      toast.error('Could not update role');
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Users</h1>
        <p className="text-slate-600">Manage all users in the system.</p>
      </div>

      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[240px] max-w-md">
          <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            className="input pl-9"
            placeholder="Search..."
            value={q}
            onChange={(e) => setQuery('search', e.target.value)}
          />
        </div>
        <select
          className="input max-w-[200px]"
          value={role}
          onChange={(e) => setQuery('role', e.target.value)}
        >
          <option value="">All roles</option>
          <option value="super_admin">Super admin</option>
          <option value="teacher">Teacher</option>
          <option value="student">Student</option>
        </select>
        <select
          className="input max-w-[200px]"
          value={isActive}
          onChange={(e) => setQuery('is_active', e.target.value)}
        >
          <option value="">Any status</option>
          <option value="true">Active</option>
          <option value="false">Disabled</option>
        </select>
      </div>

      {loading ? <Spinner /> : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">User</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Verified</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {list.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-900">{u.full_name}</td>
                  <td className="px-4 py-3">{u.email}</td>
                  <td className="px-4 py-3">
                    <select value={u.role} onChange={(e) => changeRole(u, e.target.value)} className="input py-1 text-sm">
                      <option value="super_admin">Super admin</option>
                      <option value="teacher">Teacher</option>
                      <option value="student">Student</option>
                    </select>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`badge ${u.is_active ? 'badge-success' : 'badge-danger'}`}>
                      {u.is_active ? 'Active' : 'Disabled'}
                    </span>
                  </td>
                  <td className="px-4 py-3">{u.is_email_verified ? '✅' : '⏳'}</td>
                  <td className="px-4 py-3 text-right">
                    <button className="btn-ghost text-sm" onClick={() => toggleActive(u)}>
                      {u.is_active ? 'Disable' : 'Enable'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
