import { useParams } from 'react-router-dom';
import { useFetch } from '../../hooks/useFetch';
import { attemptsApi, analyticsApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';
import { Trophy, Award, Download, MessageSquare, CheckCircle2, XCircle } from 'lucide-react';
import { downloadBlob, formatDate } from '../../utils/helpers';

export default function StudentResultDetailPage() {
  const { attemptId } = useParams();
  const { data: attempt, loading } = useFetch(() => attemptsApi.get(attemptId), [attemptId]);

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;
  if (!attempt) return <div>Result not found.</div>;

  const isPublished = attempt.status === 'published';

  const downloadPdf = async () => {
    const r = await analyticsApi.attemptPdf(attemptId);
    downloadBlob(r.data, `result-${attempt.exam_detail?.title || attemptId}.pdf`);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-primary-600 font-semibold uppercase tracking-wide">{attempt.exam_detail?.subject_name}</p>
          <h1 className="text-2xl font-bold text-slate-900">{attempt.exam_detail?.title}</h1>
          <p className="text-slate-600 text-sm">Submitted on {formatDate(attempt.submitted_at)}</p>
        </div>
        <button className="btn-secondary" onClick={downloadPdf}>
          <Download className="h-4 w-4" /> Download PDF
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Stat label="Total score" value={Number(attempt.total_score || 0).toFixed(1)} icon={Trophy} />
        <Stat label="Objective" value={Number(attempt.objective_score || 0).toFixed(1)} icon={CheckCircle2} />
        <Stat label="Descriptive" value={Number(attempt.descriptive_score || 0).toFixed(1)} icon={MessageSquare} />
        <Stat label="Status" value={isPublished ? (attempt.is_passed ? 'Passed' : 'Not passed') : attempt.status.replace('_', ' ')} icon={Award} />
      </div>

      {!isPublished && (
        <div className="card p-6 bg-amber-50 border-amber-200">
          <p className="font-semibold text-amber-800">Awaiting teacher evaluation</p>
          <p className="text-sm text-amber-700 mt-1">
            Your descriptive answers are being reviewed. The full result will appear once your teacher publishes it.
          </p>
        </div>
      )}

      <div className="card p-6">
        <h2 className="font-semibold text-slate-900 mb-4">Question-wise breakdown</h2>
        <div className="space-y-4">
          {(attempt.answers || []).map((a, i) => (
            <div key={a.id} className="border border-slate-200 rounded-xl p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <p className="text-xs uppercase font-semibold text-slate-500 tracking-wide">Q{i + 1} • {a.question_type.replace('_', ' ')} • {Number(a.question_marks).toFixed(1)} marks</p>
                  <p className="mt-1 font-medium text-slate-900">{a.question_text}</p>
                </div>
                <div className="text-right">
                  {a.is_correct === true && <span className="badge-success">Correct</span>}
                  {a.is_correct === false && <span className="badge-danger">Wrong</span>}
                  {a.is_correct === null && <span className="badge-warning">Awaiting eval</span>}
                  <p className="mt-1 text-lg font-bold text-slate-900">
                    {a.final_score !== undefined && a.final_score !== null ? Number(a.final_score).toFixed(1) : '-'}
                  </p>
                </div>
              </div>
              {a.text_answer && (
                <div className="mt-3 rounded-lg bg-slate-50 p-3 text-sm text-slate-700 whitespace-pre-wrap">{a.text_answer}</div>
              )}
              {a.code_answer && (
                <pre className="mt-3 rounded-lg bg-slate-900 text-slate-100 p-3 text-xs overflow-auto">{a.code_answer}</pre>
              )}
              {a.teacher_comment && isPublished && (
                <div className="mt-3 rounded-lg bg-primary-50 border border-primary-200 p-3 text-sm text-primary-900">
                  <p className="font-semibold flex items-center gap-1.5"><MessageSquare className="h-4 w-4" /> Teacher's comment</p>
                  <p className="mt-1">{a.teacher_comment}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value, icon: Icon }) {
  return (
    <div className="card p-5 flex items-center gap-3">
      <div className="h-10 w-10 rounded-lg bg-primary-50 text-primary-600 flex items-center justify-center">
        <Icon className="h-5 w-5" />
      </div>
      <div>
        <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
        <p className="text-lg font-bold text-slate-900">{value}</p>
      </div>
    </div>
  );
}
