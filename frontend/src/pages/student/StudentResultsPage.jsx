import { Link } from 'react-router-dom';
import { Trophy, Clock, ArrowRight } from 'lucide-react';
import { useFetch } from '../../hooks/useFetch';
import { attemptsApi, evaluationsApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';
import EmptyState from '../../components/common/EmptyState';
import { formatDate } from '../../utils/helpers';

export default function StudentResultsPage() {
  const { data: attempts, loading } = useFetch(() => attemptsApi.myAttempts(), []);
  const { data: published } = useFetch(() => evaluationsApi.myResults(), []);

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  const list = attempts?.results || attempts || [];
  const publishedIds = new Set((published?.results || published || []).map((p) => p.attempt));

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">My Results</h1>
        <p className="text-slate-600">Once your teacher publishes results, they'll show up here.</p>
      </div>

      {list.length === 0 ? (
        <EmptyState icon={Trophy} title="No attempts yet" description="Take an exam first." />
      ) : (
        <div className="card divide-y divide-slate-100">
          {list.map((a) => (
            <div key={a.id} className="flex items-center justify-between p-5">
              <div>
                <p className="font-semibold text-slate-900">{a.exam_detail?.title}</p>
                <p className="text-sm text-slate-500">{a.exam_detail?.subject_name} • {formatDate(a.submitted_at || a.started_at)}</p>
                <div className="mt-2 flex items-center gap-2">
                  <span className={`badge ${a.is_passed ? 'badge-success' : a.status === 'published' ? 'badge-warning' : 'badge-slate'} capitalize`}>
                    {a.status === 'published' ? (a.is_passed ? 'Passed' : 'Not passed') : a.status.replace('_', ' ')}
                  </span>
                  {publishedIds.has(a.id) && <span className="badge-primary">Result published</span>}
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="text-2xl font-bold text-slate-900">{Number(a.total_score || 0).toFixed(1)}</p>
                  <p className="text-xs text-slate-500">/ {Number(a.exam_detail?.total_marks || 0).toFixed(0)}</p>
                </div>
                <Link to={`/results/${a.id}`} className="btn-primary">
                  View <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
