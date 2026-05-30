import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { BookOpen, Clock, ArrowRight, AlertTriangle } from 'lucide-react';
import { useFetch } from '../../hooks/useFetch';
import { attemptsApi, examsApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';
import EmptyState from '../../components/common/EmptyState';
import { formatDate } from '../../utils/helpers';

export default function StudentExamsPage() {
  const navigate = useNavigate();
  const { data: exams, loading } = useFetch(() => examsApi.list({ ordering: 'start_time' }), []);
  const list = exams?.results || exams || [];

  const startExam = async (slug, exam) => {
    try {
      const res = await attemptsApi.start(exam.id);
      navigate(`/exams/${slug}/attempt`, { state: { attempt: res.data } });
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Could not start attempt');
    }
  };

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">My Exams</h1>
        <p className="text-slate-600">Exams you are enrolled in.</p>
      </div>

      {list.length === 0 ? (
        <EmptyState
          icon={BookOpen}
          title="No exams yet"
          description="Once your teacher publishes an exam and enrolls you, it will appear here."
        />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {list.map((exam) => (
            <div key={exam.id} className="card-hover p-5 flex flex-col">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs uppercase tracking-wide text-primary-600 font-semibold">
                    {exam.subject_name || exam.subject_detail?.name}
                  </p>
                  <h3 className="mt-1 font-semibold text-slate-900">{exam.title}</h3>
                </div>
                <span className={`badge ${
                  exam.status === 'live' ? 'badge-success' :
                  exam.status === 'scheduled' ? 'badge-primary' :
                  exam.status === 'completed' ? 'badge-slate' : 'badge-warning'
                } capitalize`}>{exam.status}</span>
              </div>

              <div className="mt-4 space-y-2 text-sm text-slate-600">
                <div className="flex items-center gap-2"><Clock className="h-4 w-4" /> {exam.duration_minutes} min</div>
                <div className="flex items-center gap-2"><Clock className="h-4 w-4" /> Window: {formatDate(exam.start_time)} → {formatDate(exam.end_time)}</div>
                <div className="text-xs text-slate-500">Marks: {exam.total_marks} • Pass: {exam.passing_marks}</div>
              </div>

              <button
                className="btn-primary mt-5 self-start"
                disabled={exam.status === 'archived' || exam.status === 'completed'}
                onClick={() => startExam(exam.slug, exam)}
              >
                Start exam <ArrowRight className="h-4 w-4" />
              </button>
              {exam.enable_proctoring && (
                <p className="mt-3 flex items-center gap-1.5 text-xs text-amber-700">
                  <AlertTriangle className="h-3.5 w-3.5" /> Proctored: fullscreen + tab tracking
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
