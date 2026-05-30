import { useMemo } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Plus, Edit2, Trash2, BookOpen, Search } from 'lucide-react';
import toast from 'react-hot-toast';
import { useFetch } from '../../hooks/useFetch';
import { examsApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';
import EmptyState from '../../components/common/EmptyState';
import { formatDate } from '../../utils/helpers';

const STATUSES = [
  { value: '', label: 'All statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'scheduled', label: 'Scheduled' },
  { value: 'live', label: 'Live' },
  { value: 'completed', label: 'Completed' },
  { value: 'archived', label: 'Archived' },
];

export default function TeacherExamsPage() {
  const navigate = useNavigate();
  const [params, setParams] = useSearchParams();
  const status = params.get('status') || '';
  const search = params.get('search') || '';

  const apiParams = useMemo(() => {
    const p = { ordering: '-created_at' };
    if (status) p.status = status;
    if (search) p.search = search;
    return p;
  }, [status, search]);

  const { data, loading, setData } = useFetch(() => examsApi.list(apiParams), [status, search]);
  const list = data?.results || data || [];

  const setQuery = (key, value) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    setParams(next);
  };

  const remove = async (slug) => {
    if (!confirm('Delete this exam?')) return;
    try {
      await examsApi.remove(slug);
      setData({ ...(data || {}), results: list.filter((e) => e.slug !== slug) });
      toast.success('Exam deleted');
    } catch {
      toast.error('Could not delete');
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Exams</h1>
          <p className="text-slate-600">Create, schedule and publish exams for your students.</p>
        </div>
        <Link to="/exams/new" className="btn-primary">
          <Plus className="h-4 w-4" /> New exam
        </Link>
      </div>

      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[240px] max-w-md">
          <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            className="input pl-9"
            placeholder="Search title or subject…"
            value={search}
            onChange={(e) => setQuery('search', e.target.value)}
          />
        </div>
        <select
          value={status}
          onChange={(e) => setQuery('status', e.target.value)}
          className="input max-w-[200px]"
        >
          {STATUSES.map((s) => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="flex justify-center py-20"><Spinner size="lg" /></div>
      ) : list.length === 0 ? (
        <EmptyState
          icon={BookOpen}
          title={status || search ? 'No matching exams' : 'No exams yet'}
          description={status || search
            ? 'Try clearing the filters or creating a new exam.'
            : 'Create your first exam to get started.'}
          action={<Link to="/exams/new" className="btn-primary"><Plus className="h-4 w-4" /> Create exam</Link>}
        />
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Title</th>
                <th className="px-4 py-3">Subject</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Window</th>
                <th className="px-4 py-3">Questions</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {list.map((e) => (
                <tr key={e.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-900">
                    <Link to={`/exams/${e.slug}/edit`} className="hover:text-primary-600">{e.title}</Link>
                  </td>
                  <td className="px-4 py-3">{e.subject_name}</td>
                  <td className="px-4 py-3 capitalize">{e.exam_type}</td>
                  <td className="px-4 py-3">
                    <span className={`badge ${
                      e.status === 'live' ? 'badge-success' :
                      e.status === 'scheduled' ? 'badge-primary' :
                      e.status === 'completed' ? 'badge-slate' : 'badge-warning'
                    } capitalize`}>{e.status}</span>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500">
                    {formatDate(e.start_time)}<br/>→ {formatDate(e.end_time)}
                  </td>
                  <td className="px-4 py-3">{e.question_count}</td>
                  <td className="px-4 py-3 text-right">
                    <div className="inline-flex gap-1">
                      <button onClick={() => navigate(`/exams/${e.slug}/edit`)} className="btn-ghost p-2"><Edit2 className="h-4 w-4" /></button>
                      <button onClick={() => remove(e.slug)} className="btn-ghost p-2 text-red-600 hover:bg-red-50"><Trash2 className="h-4 w-4" /></button>
                    </div>
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
