import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import Editor from '@monaco-editor/react';
import {
  ChevronLeft, ChevronRight, Send, Clock, Maximize2, AlertTriangle, Save, Play, Loader2,
} from 'lucide-react';
import { attemptsApi, examsApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';

const QUESTION_TYPE_LABEL = {
  single_choice: 'Single Choice',
  multiple_choice: 'Multiple Choice',
  true_false: 'True / False',
  fill_blank: 'Fill in the Blank',
  descriptive: 'Descriptive',
  coding: 'Coding',
};

export default function StudentExamAttemptPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { slug } = useParams();

  const [attempt, setAttempt] = useState(location.state?.attempt || null);
  const [exam, setExam] = useState(null);
  const [loading, setLoading] = useState(!attempt);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [tabSwitches, setTabSwitches] = useState(0);
  const containerRef = useRef(null);

  // Bootstrapping: fetch exam (for proctoring flag) + create attempt if needed
  useEffect(() => {
    let cancelled = false;
    async function init() {
      try {
        const examRes = await examsApi.get(slug);
        if (!cancelled) setExam(examRes.data);
        if (!attempt) {
          const created = await attemptsApi.start(examRes.data.id);
          if (!cancelled) setAttempt(created.data);
        }
      } catch (err) {
        toast.error(err.response?.data?.detail || 'Failed to load exam');
        navigate('/exams');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    init();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slug]);

  // Build a map of existing answers so navigation preserves them
  useEffect(() => {
    if (!attempt?.answers) return;
    const seed = {};
    for (const a of attempt.answers) {
      seed[a.question] = {
        selected_options: a.selected_options || [],
        text_answer: a.text_answer || '',
        code_answer: a.code_answer || '',
        code_language: a.code_language || '',
      };
    }
    setAnswers(seed);
  }, [attempt?.id]);  // eslint-disable-line

  const questions = attempt?.questions || [];
  const currentQuestion = questions[currentIdx];

  // ----- Timer -----
  const endTime = useMemo(() => {
    if (!attempt || !exam) return null;
    return new Date(new Date(attempt.started_at).getTime() + exam.duration_minutes * 60 * 1000);
  }, [attempt, exam]);

  const [timeLeft, setTimeLeft] = useState('00:00:00');
  useEffect(() => {
    if (!endTime) return;
    const tick = () => {
      const ms = endTime.getTime() - Date.now();
      if (ms <= 0) {
        setTimeLeft('00:00:00');
        handleSubmit(true);
        return;
      }
      const totalSeconds = Math.floor(ms / 1000);
      const h = String(Math.floor(totalSeconds / 3600)).padStart(2, '0');
      const m = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, '0');
      const s = String(totalSeconds % 60).padStart(2, '0');
      setTimeLeft(`${h}:${m}:${s}`);
    };
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [endTime]);

  // ----- Anti cheating -----
  const requestFullscreen = useCallback(() => {
    const el = containerRef.current || document.documentElement;
    if (el.requestFullscreen) el.requestFullscreen().catch(() => {});
  }, []);

  useEffect(() => {
    if (!exam?.enable_proctoring || !attempt) return;
    requestFullscreen();

    const reportEvent = (eventType, metadata = {}) => {
      attemptsApi.proctorEvent(attempt.id, eventType, metadata).catch(() => {});
    };

    const onVisibility = () => {
      if (document.hidden) {
        setTabSwitches((c) => c + 1);
        toast.error('Switching tabs is not allowed during the exam.');
        reportEvent('tab_switch');
      }
    };
    const onFsChange = () => {
      if (!document.fullscreenElement) {
        toast.error('Please remain in fullscreen mode.');
        reportEvent('fullscreen_exit');
      }
    };
    const onContextMenu = (e) => {
      e.preventDefault();
      reportEvent('right_click');
    };
    const onKey = (e) => {
      if ((e.ctrlKey || e.metaKey) && ['c', 'v', 'x'].includes(e.key.toLowerCase())) {
        if (currentQuestion?.question_type === 'coding') return;
        e.preventDefault();
        reportEvent('copy_paste', { key: e.key });
      }
    };
    document.addEventListener('visibilitychange', onVisibility);
    document.addEventListener('fullscreenchange', onFsChange);
    document.addEventListener('contextmenu', onContextMenu);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('visibilitychange', onVisibility);
      document.removeEventListener('fullscreenchange', onFsChange);
      document.removeEventListener('contextmenu', onContextMenu);
      document.removeEventListener('keydown', onKey);
    };
  }, [exam?.enable_proctoring, attempt, currentQuestion?.question_type, requestFullscreen]);

  // ----- Answer helpers -----
  const updateAnswer = (qid, patch) => {
    setAnswers((prev) => ({ ...prev, [qid]: { ...prev[qid], ...patch } }));
  };

  const saveAnswer = useCallback(async (qid) => {
    if (!attempt) return;
    const ans = answers[qid] || {};
    const payload = {
      question: qid,
      selected_options: ans.selected_options || [],
      text_answer: ans.text_answer || '',
      code_answer: ans.code_answer || '',
      code_language: ans.code_language || '',
    };
    try {
      await attemptsApi.saveAnswer(attempt.id, payload);
    } catch (err) {
      toast.error('Could not save your answer');
    }
  }, [answers, attempt]);

  const handleSubmit = useCallback(async (auto = false) => {
    if (!attempt || submitting) return;
    setSubmitting(true);
    try {
      // save current first
      if (currentQuestion) {
        await saveAnswer(currentQuestion.id);
      }
      const res = await attemptsApi.submit(attempt.id, auto);
      toast.success(auto ? 'Time over - exam auto-submitted' : 'Exam submitted!');
      if (document.fullscreenElement) document.exitFullscreen?.().catch(() => {});
      navigate(`/results/${res.data.id}`);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Could not submit');
      setSubmitting(false);
    }
  }, [attempt, currentQuestion, navigate, saveAnswer, submitting]);

  // Auto-save on question change
  const goTo = async (idx) => {
    if (currentQuestion) await saveAnswer(currentQuestion.id);
    setCurrentIdx(idx);
  };

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;
  if (!attempt || !currentQuestion) return null;

  return (
    <div ref={containerRef} className="fixed inset-0 z-40 bg-slate-50 flex flex-col">
      {/* Top bar */}
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-primary-600 font-semibold">{exam?.subject_detail?.name || exam?.subject_name}</p>
          <h1 className="font-bold text-slate-900">{exam?.title}</h1>
        </div>
        <div className="flex items-center gap-4">
          {tabSwitches > 0 && (
            <span className="badge-warning flex items-center gap-1">
              <AlertTriangle className="h-3.5 w-3.5" /> Tab switches: {tabSwitches}
            </span>
          )}
          <button onClick={requestFullscreen} className="btn-ghost" title="Fullscreen">
            <Maximize2 className="h-4 w-4" />
          </button>
          <div className={`flex items-center gap-2 rounded-lg px-3 py-1.5 font-mono font-semibold ${
            timeLeft.startsWith('00:0') && timeLeft <= '00:05:00' ? 'bg-red-50 text-red-700' : 'bg-slate-100 text-slate-700'
          }`}>
            <Clock className="h-4 w-4" /> {timeLeft}
          </div>
          <button onClick={() => handleSubmit(false)} disabled={submitting} className="btn-primary">
            {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            Submit
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Question palette */}
        <aside className="hidden lg:flex w-64 flex-col border-r border-slate-200 bg-white p-4">
          <p className="text-xs uppercase tracking-wide text-slate-500 mb-3 font-semibold">Questions</p>
          <div className="grid grid-cols-5 gap-2">
            {questions.map((q, i) => {
              const ans = answers[q.id];
              const answered = ans && (
                ans.selected_options?.length || ans.text_answer || ans.code_answer
              );
              return (
                <button
                  key={q.id}
                  onClick={() => goTo(i)}
                  className={`h-9 w-9 rounded-lg text-sm font-semibold transition ${
                    i === currentIdx
                      ? 'bg-primary-600 text-white shadow-glow'
                      : answered
                        ? 'bg-emerald-100 text-emerald-700 hover:bg-emerald-200'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  {i + 1}
                </button>
              );
            })}
          </div>
          <div className="mt-6 space-y-2 text-xs text-slate-500">
            <div className="flex items-center gap-2"><span className="h-3 w-3 rounded bg-primary-600 inline-block" /> Current</div>
            <div className="flex items-center gap-2"><span className="h-3 w-3 rounded bg-emerald-200 inline-block" /> Answered</div>
            <div className="flex items-center gap-2"><span className="h-3 w-3 rounded bg-slate-200 inline-block" /> Not answered</div>
          </div>
        </aside>

        {/* Question area */}
        <section className="flex-1 overflow-y-auto p-6">
          <div className="mx-auto max-w-4xl">
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-slate-500">
                Question {currentIdx + 1} of {questions.length} • {QUESTION_TYPE_LABEL[currentQuestion.question_type]}
              </p>
              <p className="text-sm font-semibold text-slate-700">Marks: {currentQuestion.marks}</p>
            </div>

            <h2 className="text-lg font-semibold text-slate-900 leading-relaxed whitespace-pre-wrap">
              {currentQuestion.text}
            </h2>
            {currentQuestion.image && (
              <img src={currentQuestion.image} alt="" className="mt-4 rounded-lg border border-slate-200 max-h-80" />
            )}

            <div className="mt-6">
              <QuestionRenderer
                question={currentQuestion}
                value={answers[currentQuestion.id] || {}}
                onChange={(patch) => updateAnswer(currentQuestion.id, patch)}
                attemptId={attempt.id}
              />
            </div>

            <div className="mt-8 flex items-center justify-between">
              <button onClick={() => goTo(Math.max(0, currentIdx - 1))} disabled={currentIdx === 0} className="btn-secondary">
                <ChevronLeft className="h-4 w-4" /> Previous
              </button>
              <button onClick={() => saveAnswer(currentQuestion.id).then(() => toast.success('Saved'))} className="btn-ghost">
                <Save className="h-4 w-4" /> Save answer
              </button>
              <button onClick={() => goTo(Math.min(questions.length - 1, currentIdx + 1))} disabled={currentIdx >= questions.length - 1} className="btn-primary">
                Next <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

function QuestionRenderer({ question, value, onChange, attemptId }) {
  const t = question.question_type;
  const opts = question.options || [];

  if (t === 'single_choice' || t === 'true_false') {
    const selected = value.selected_options?.[0];
    return (
      <ul className="space-y-2">
        {opts.map((o) => (
          <li key={o.id}>
            <label className={`flex items-center gap-3 rounded-lg border px-4 py-3 cursor-pointer transition ${selected === o.id ? 'border-primary-500 bg-primary-50' : 'border-slate-300 hover:bg-slate-50'}`}>
              <input
                type="radio"
                name={question.id}
                value={o.id}
                checked={selected === o.id}
                onChange={() => onChange({ selected_options: [o.id] })}
                className="h-4 w-4 text-primary-600"
              />
              <span className="text-slate-800">{o.text}</span>
            </label>
          </li>
        ))}
      </ul>
    );
  }

  if (t === 'multiple_choice') {
    const selected = new Set(value.selected_options || []);
    const toggle = (id) => {
      const next = new Set(selected);
      if (next.has(id)) next.delete(id); else next.add(id);
      onChange({ selected_options: Array.from(next) });
    };
    return (
      <ul className="space-y-2">
        {opts.map((o) => (
          <li key={o.id}>
            <label className={`flex items-center gap-3 rounded-lg border px-4 py-3 cursor-pointer transition ${selected.has(o.id) ? 'border-primary-500 bg-primary-50' : 'border-slate-300 hover:bg-slate-50'}`}>
              <input
                type="checkbox"
                checked={selected.has(o.id)}
                onChange={() => toggle(o.id)}
                className="h-4 w-4 rounded text-primary-600"
              />
              <span className="text-slate-800">{o.text}</span>
            </label>
          </li>
        ))}
      </ul>
    );
  }

  if (t === 'fill_blank') {
    return (
      <input
        type="text"
        value={value.text_answer || ''}
        onChange={(e) => onChange({ text_answer: e.target.value })}
        className="input"
        placeholder="Type your answer..."
      />
    );
  }

  if (t === 'descriptive') {
    return (
      <textarea
        rows={10}
        value={value.text_answer || ''}
        onChange={(e) => onChange({ text_answer: e.target.value })}
        className="input font-sans"
        placeholder="Type your answer here..."
      />
    );
  }

  if (t === 'coding') {
    return (
      <CodingQuestion
        question={question}
        value={value}
        onChange={onChange}
        attemptId={attemptId}
      />
    );
  }

  return null;
}

function CodingQuestion({ question, value, onChange, attemptId }) {
  const lang = question.coding_language || 'python';
  const monacoLang = { python: 'python', sql: 'sql', pyspark: 'python', java: 'java' }[lang] || 'python';
  const [runResult, setRunResult] = useState(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    if (!value.code_answer && question.starter_code) {
      onChange({ code_answer: question.starter_code, code_language: lang });
    } else if (!value.code_language) {
      onChange({ code_language: lang });
    }
  }, []); // eslint-disable-line

  const run = async () => {
    setRunning(true);
    try {
      const res = await attemptsApi.runCode(attemptId, {
        question_id: question.id,
        code: value.code_answer,
        language: lang,
      });
      setRunResult(res.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Code execution failed');
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span className="badge-primary uppercase">
          {{ python: 'Python', sql: 'SQL Server', pyspark: 'PySpark', java: 'Java' }[lang] || lang}
        </span>
        <button onClick={run} className="btn-secondary" disabled={running}>
          {running ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />} Run sample tests
        </button>
      </div>
      <div className="overflow-hidden rounded-xl border border-slate-300">
        <Editor
          height="400px"
          theme="vs-dark"
          language={monacoLang}
          value={value.code_answer || question.starter_code || ''}
          onChange={(v) => onChange({ code_answer: v ?? '', code_language: lang })}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            scrollBeyondLastLine: false,
            tabSize: 4,
          }}
        />
      </div>
      {runResult && (
        <div className="card p-4 bg-slate-900 text-slate-100 font-mono text-xs space-y-2 max-h-60 overflow-auto">
          <p className="text-emerald-400 font-semibold">Passed: {runResult.passed} / {runResult.total}</p>
          {runResult.message && <p className="text-amber-300">{runResult.message}</p>}
          {(runResult.details || []).map((d, i) => (
            <div key={i} className={d.passed ? 'text-emerald-300' : 'text-red-300'}>
              <p>Test #{i + 1}: {d.passed ? 'PASS' : 'FAIL'}</p>
              <p>Input: {JSON.stringify(d.input)}</p>
              <p>Expected: {d.expected}</p>
              <p>Actual: {d.actual}</p>
              {d.stderr && <p>Stderr: {d.stderr}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
