import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Send, Sparkles, Save, ArrowLeft } from 'lucide-react';
import { aiApi, evaluationsApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';

export default function TeacherEvaluationDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [overall, setOverall] = useState('');
  const [savingId, setSavingId] = useState(null);
  const [aiBusyId, setAiBusyId] = useState(null);
  const [publishing, setPublishing] = useState(false);

  useEffect(() => {
    evaluationsApi
      .get(id)
      .then((r) => {
        setEvaluation(r.data);
        setOverall(r.data.overall_comment || '');
      })
      .catch(() => toast.error('Could not load evaluation'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;
  if (!evaluation) return null;

  const updateAnswerLocally = (answerId, patch) => {
    setEvaluation({
      ...evaluation,
      answers: evaluation.answers.map((a) => (a.id === answerId ? { ...a, ...patch } : a)),
    });
  };

  const grade = async (a) => {
    setSavingId(a.id);
    try {
      const score = a.manual_score === null || a.manual_score === '' ? 0 : Number(a.manual_score);
      const r = await evaluationsApi.gradeAnswer(id, {
        answer_id: a.id,
        manual_score: score,
        teacher_comment: a.teacher_comment || '',
      });
      setEvaluation((prev) => ({ ...prev, total_score: r.data.total_score }));
      toast.success('Saved');
    } catch {
      toast.error('Could not save');
    } finally {
      setSavingId(null);
    }
  };

  const aiGrade = async (a) => {
    setAiBusyId(a.id);
    try {
      const r = await aiApi.chat([
        { role: 'system', content: 'You are an exam evaluator. Return only a number representing suggested marks (no text).' },
        {
          role: 'user',
          content: `Question: ${a.question_text}\nMax marks: ${a.question_marks}\nStudent answer: ${a.text_answer || '(no text)'}\n\nReturn only the suggested marks (numeric).`,
        },
      ]);
      const content = (r.data?.response || '').replace(/[^0-9.]/g, '');
      const suggested = parseFloat(content);
      if (!Number.isNaN(suggested)) {
        updateAnswerLocally(a.id, { manual_score: suggested });
        toast.success(`AI suggested ${suggested.toFixed(2)} marks`);
      } else {
        toast.error('AI returned non-numeric output');
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'AI grading failed');
    } finally {
      setAiBusyId(null);
    }
  };

  const publish = async () => {
    setPublishing(true);
    try {
      await evaluationsApi.publish(id, true);
      toast.success('Result published. Student has been notified.');
      navigate('/evaluations');
    } catch {
      toast.error('Could not publish');
    } finally {
      setPublishing(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <button onClick={() => navigate('/evaluations')} className="btn-ghost">
          <ArrowLeft className="h-4 w-4" /> Back
        </button>
        <button onClick={publish} disabled={publishing} className="btn-primary">
          <Send className="h-4 w-4" /> {publishing ? 'Publishing...' : 'Publish result'}
        </button>
      </div>

      <div className="card p-6">
        <h1 className="text-xl font-bold text-slate-900">{evaluation.exam_title}</h1>
        <p className="text-slate-600 text-sm">Student: {evaluation.student_name} ({evaluation.student_email})</p>
        <div className="mt-4 grid grid-cols-3 gap-3 text-sm">
          <Stat label="Objective" value={Number(evaluation.objective_score || 0).toFixed(1)} />
          <Stat label="Descriptive" value={Number(evaluation.descriptive_score || 0).toFixed(1)} />
          <Stat label="Total" value={Number(evaluation.total_score || 0).toFixed(1)} />
        </div>
      </div>

      <div className="space-y-3">
        {evaluation.answers.map((a, i) => (
          <div key={a.id} className="card p-5">
            <p className="text-xs uppercase font-semibold text-slate-500 tracking-wide">
              Q{i + 1} • {a.question_type.replace('_', ' ')} • {Number(a.question_marks).toFixed(1)} marks
            </p>
            <p className="mt-1 font-medium text-slate-900">{a.question_text}</p>

            {a.text_answer && (
              <div className="mt-3 rounded-lg bg-slate-50 p-3 text-sm text-slate-700 whitespace-pre-wrap">{a.text_answer}</div>
            )}
            {a.code_answer && (
              <pre className="mt-3 rounded-lg bg-slate-900 text-slate-100 p-3 text-xs overflow-auto">{a.code_answer}</pre>
            )}
            {a.uploaded_file && (
              <a href={a.uploaded_file} target="_blank" rel="noreferrer" className="mt-2 inline-block text-primary-600 text-sm">
                📎 View attached file
              </a>
            )}

            {(a.question_type === 'descriptive' || a.question_type === 'coding') && (
              <div className="mt-4 grid gap-3 md:grid-cols-3">
                <div>
                  <label className="label">Marks (max {a.question_marks})</label>
                  <input
                    type="number" step="0.5" max={a.question_marks} min={0}
                    className="input"
                    value={a.manual_score ?? ''}
                    onChange={(e) => updateAnswerLocally(a.id, { manual_score: e.target.value })}
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="label">Comment</label>
                  <input
                    className="input"
                    value={a.teacher_comment || ''}
                    onChange={(e) => updateAnswerLocally(a.id, { teacher_comment: e.target.value })}
                    placeholder="Feedback for student..."
                  />
                </div>
                <div className="md:col-span-3 flex gap-2">
                  <button onClick={() => grade(a)} className="btn-primary" disabled={savingId === a.id}>
                    <Save className="h-4 w-4" /> Save
                  </button>
                  <button onClick={() => aiGrade(a)} className="btn-secondary" disabled={aiBusyId === a.id}>
                    <Sparkles className="h-4 w-4" /> {aiBusyId === a.id ? 'Asking AI...' : 'AI suggest marks'}
                  </button>
                </div>
              </div>
            )}

            {(a.question_type !== 'descriptive' && a.question_type !== 'coding') && (
              <p className="mt-3 text-sm text-slate-500">Auto-graded: {a.is_correct ? '✅ correct' : '❌ wrong'} — {Number(a.auto_score).toFixed(1)} marks</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="rounded-lg bg-primary-50 p-3 text-center">
      <p className="text-xs text-primary-700">{label}</p>
      <p className="text-lg font-bold text-primary-900">{value}</p>
    </div>
  );
}
