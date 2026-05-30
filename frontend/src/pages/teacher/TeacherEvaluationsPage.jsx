import { Link } from 'react-router-dom';
import { ArrowRight, ClipboardList } from 'lucide-react';
import toast from 'react-hot-toast';
import { useFetch } from '../../hooks/useFetch';
import { attemptsApi, evaluationsApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';
import EmptyState from '../../components/common/EmptyState';
import { formatDate } from '../../utils/helpers';

export default function TeacherEvaluationsPage() {
  const { data: attempts, loading } = useFetch(() => attemptsApi.pendingEvaluation(), []);
  const list = attempts?.results || attempts || [];

  const startEvaluation = async (attemptId) => {
    try {
      const r = await evaluationsApi.fromAttempt(attemptId);
      window.location.href = `/evaluations/${r.data.id}`;
    } catch {
      toast.error('Could not open evaluation');
    }
  };

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Evaluations</h1>
        <p className="text-slate-600">Attempts pending manual evaluation.</p>
      </div>

      {list.length === 0 ? (
        <EmptyState icon={ClipboardList} title="Nothing pending" description="All submitted exams have been evaluated. " />
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Student</th>
                <th className="px-4 py-3">Exam</th>
                <th className="px-4 py-3">Submitted</th>
                <th className="px-4 py-3">Auto score</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {list.map((a) => (
                <tr key={a.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-900">{a.student_name}<br /><span className="text-xs text-slate-500">{a.student_email}</span></td>
                  <td className="px-4 py-3">{a.exam_detail?.title}</td>
                  <td className="px-4 py-3 text-xs">{formatDate(a.submitted_at)}</td>
                  <td className="px-4 py-3">{Number(a.objective_score).toFixed(1)}</td>
                  <td className="px-4 py-3"><span className="badge-warning capitalize">{a.status.replace('_', ' ')}</span></td>
                  <td className="px-4 py-3 text-right">
                    <button onClick={() => startEvaluation(a.id)} className="btn-primary">
                      Evaluate <ArrowRight className="h-4 w-4" />
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
