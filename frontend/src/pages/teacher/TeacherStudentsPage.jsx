import { useEffect, useState } from 'react';
import { Search, Mail, Phone } from 'lucide-react';
import { useFetch } from '../../hooks/useFetch';
import { usersApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';
import { formatApiError } from '../../utils/helpers';

function useDebouncedValue(value, delayMs = 350) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(id);
  }, [value, delayMs]);
  return debounced;
}

export default function TeacherStudentsPage() {
  const [q, setQ] = useState('');
  const search = useDebouncedValue(q.trim());
  const { data, loading, error } = useFetch(
    () =>
      usersApi.list({
        role: 'student',
        search: search || undefined,
        page_size: 100,
      }),
    [search],
  );
  const list = data?.results || [];
  const total = data?.count ?? list.length;

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Students</h1>
        <p className="text-slate-600">Browse and search registered students (teachers and admins only).</p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative max-w-md flex-1 min-w-[200px]">
          <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            className="input pl-9"
            placeholder="Name, email, enrollment ID, batch..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
        {!loading && (
          <p className="text-sm text-slate-500">
            {total} student{total === 1 ? '' : 's'}
            {search ? ` matching "${search}"` : ''}
          </p>
        )}
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          {formatApiError(error)}
        </div>
      )}

      {loading ? (
        <Spinner />
      ) : list.length === 0 ? (
        <div className="card p-8 text-center text-slate-600">
          {search ? (
            <p>No students found for &quot;{search}&quot;. Try name, email, or enrollment ID.</p>
          ) : (
            <p>No students registered yet. Students appear here after they sign up or an admin creates them.</p>
          )}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {list.map((u) => (
            <div key={u.id} className="card-hover p-5">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-full bg-gradient-to-br from-primary-500 to-primary-700 text-white flex items-center justify-center font-bold">
                  {(u.first_name?.[0] || u.email[0]).toUpperCase()}
                </div>
                <div>
                  <p className="font-semibold text-slate-900">{u.full_name}</p>
                  <p className="text-xs text-slate-500">{u.student_profile?.enrollment_id}</p>
                </div>
              </div>
              <div className="mt-3 space-y-1 text-sm text-slate-600">
                <p className="flex items-center gap-2">
                  <Mail className="h-4 w-4" /> {u.email}
                </p>
                {u.phone && (
                  <p className="flex items-center gap-2">
                    <Phone className="h-4 w-4" /> {u.phone}
                  </p>
                )}
                {u.student_profile?.batch && (
                  <p className="text-xs text-slate-500">Batch: {u.student_profile.batch}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
