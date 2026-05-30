import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Plus, Save, Send, Users, Trash2, Edit2 } from 'lucide-react';
import { examsApi, questionsApi, subjectsApi, usersApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';
import Modal from '../../components/common/Modal';
import CodeStudioEditor from '../../components/code/CodeStudioEditor';
import { monacoLanguageFor } from '../../constants/codeStudioLanguages';
import { formatApiError } from '../../utils/helpers';

const EXAM_TYPE = ['mixed', 'objective', 'descriptive', 'coding'];
const QUESTION_TYPES = [
  { value: 'single_choice', label: 'Single Choice' },
  { value: 'multiple_choice', label: 'Multiple Choice' },
  { value: 'true_false', label: 'True / False' },
  { value: 'fill_blank', label: 'Fill in the Blank' },
  { value: 'descriptive', label: 'Descriptive' },
  { value: 'coding', label: 'Coding' },
];
const CODING_LANGUAGES = [
  { value: 'python', label: 'Python' },
  { value: 'sql', label: 'SQL Server' },
  { value: 'pyspark', label: 'PySpark' },
  { value: 'java', label: 'Java' },
];
const DIFFICULTY = ['easy', 'medium', 'hard'];

export default function TeacherExamEditorPage() {
  const { slug } = useParams();
  const isNew = !slug;
  const navigate = useNavigate();
  const [exam, setExam] = useState(null);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [editingQuestion, setEditingQuestion] = useState(null);
  const [enrollOpen, setEnrollOpen] = useState(false);

  useEffect(() => {
    subjectsApi.list({ is_active: true }).then((r) => setSubjects(r.data?.results || r.data || []));
  }, []);

  useEffect(() => {
    if (isNew) {
      const now = new Date();
      const future = new Date(now.getTime() + 7 * 24 * 3600 * 1000);
      setExam({
        title: '',
        description: '',
        instructions: '',
        subject: '',
        exam_type: 'mixed',
        status: 'draft',
        duration_minutes: 60,
        total_marks: 0,
        passing_marks: 0,
        negative_marking: 0,
        randomize_questions: false,
        randomize_options: false,
        show_results_immediately: false,
        allow_retake: false,
        enable_proctoring: true,
        start_time: toLocalInput(now),
        end_time: toLocalInput(future),
      });
      return;
    }
    examsApi
      .get(slug)
      .then((r) => {
        setExam({
          ...r.data,
          subject: r.data.subject,
          start_time: toLocalInput(r.data.start_time),
          end_time: toLocalInput(r.data.end_time),
        });
        return questionsApi.list({ exam: r.data.id }).then((qr) => {
          setQuestions(qr.data?.results || qr.data || []);
        });
      })
      .catch(() => toast.error('Could not load exam'))
      .finally(() => setLoading(false));
  }, [slug, isNew]);

  const onChange = (e) => {
    const { name, value, type, checked } = e.target;
    setExam((prev) => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const save = async () => {
    if (!exam.title || !exam.subject) {
      return toast.error('Title and subject are required');
    }
    setSaving(true);
    try {
      const payload = {
        ...exam,
        start_time: new Date(exam.start_time).toISOString(),
        end_time: new Date(exam.end_time).toISOString(),
      };
      if (isNew) {
        const r = await examsApi.create(payload);
        toast.success('Exam created');
        navigate(`/exams/${r.data.slug}/edit`, { replace: true });
      } else {
        await examsApi.update(slug, payload);
        toast.success('Exam saved');
      }
    } catch (err) {
      toast.error(formatApiError(err, 'Could not save exam'));
    } finally {
      setSaving(false);
    }
  };

  const publish = async (status) => {
    try {
      await examsApi.publish(slug, status);
      setExam({ ...exam, status });
      toast.success(`Status updated to ${status}`);
    } catch {
      toast.error('Could not update status');
    }
  };

  const reloadQuestions = async () => {
    if (!exam?.id) return;
    const r = await questionsApi.list({ exam: exam.id });
    setQuestions(r.data?.results || r.data || []);
  };

  const removeQuestion = async (id) => {
    if (!confirm('Delete this question?')) return;
    await questionsApi.remove(id);
    reloadQuestions();
  };

  if (loading || !exam) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <Link to="/exams" className="text-sm text-primary-600 hover:text-primary-700">← Back to exams</Link>
          <h1 className="text-2xl font-bold text-slate-900 mt-1">{isNew ? 'New exam' : exam.title}</h1>
        </div>
        <div className="flex items-center gap-2">
          {!isNew && (
            <>
              <button onClick={() => setEnrollOpen(true)} className="btn-secondary">
                <Users className="h-4 w-4" /> Enroll students
              </button>
              <select
                value={exam.status}
                onChange={(e) => publish(e.target.value)}
                className="input max-w-[160px]"
              >
                <option value="draft">Draft</option>
                <option value="scheduled">Scheduled</option>
                <option value="live">Live</option>
                <option value="completed">Completed</option>
                <option value="archived">Archived</option>
              </select>
            </>
          )}
          <button onClick={save} className="btn-primary" disabled={saving}>
            <Save className="h-4 w-4" /> {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>

      <div className="card p-6 grid gap-4 md:grid-cols-2">
        <div className="md:col-span-2">
          <label className="label">Title</label>
          <input className="input" name="title" value={exam.title} onChange={onChange} />
        </div>
        <div>
          <label className="label">Subject</label>
          <select className="input" name="subject" value={exam.subject || ''} onChange={onChange}>
            <option value="">Select a subject...</option>
            {subjects.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </div>
        <div>
          <label className="label">Exam type</label>
          <select className="input" name="exam_type" value={exam.exam_type} onChange={onChange}>
            {EXAM_TYPE.map((t) => <option key={t} value={t} className="capitalize">{t}</option>)}
          </select>
        </div>
        <div>
          <label className="label">Duration (minutes)</label>
          <input type="number" className="input" name="duration_minutes" value={exam.duration_minutes} onChange={onChange} />
        </div>
        <div>
          <label className="label">Total marks</label>
          <input type="number" step="0.5" className="input" name="total_marks" value={exam.total_marks} onChange={onChange} />
        </div>
        <div>
          <label className="label">Passing marks</label>
          <input type="number" step="0.5" className="input" name="passing_marks" value={exam.passing_marks} onChange={onChange} />
        </div>
        <div>
          <label className="label">Negative marking</label>
          <input type="number" step="0.25" className="input" name="negative_marking" value={exam.negative_marking} onChange={onChange} />
        </div>
        <div>
          <label className="label">Start time</label>
          <input type="datetime-local" className="input" name="start_time" value={exam.start_time} onChange={onChange} />
        </div>
        <div>
          <label className="label">End time</label>
          <input type="datetime-local" className="input" name="end_time" value={exam.end_time} onChange={onChange} />
        </div>
        <div className="md:col-span-2">
          <label className="label">Description</label>
          <textarea rows={2} className="input" name="description" value={exam.description} onChange={onChange} />
        </div>
        <div className="md:col-span-2">
          <label className="label">Instructions to students</label>
          <textarea rows={3} className="input" name="instructions" value={exam.instructions} onChange={onChange} />
        </div>
        <div className="md:col-span-2 grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
          <Toggle name="randomize_questions" checked={exam.randomize_questions} onChange={onChange} label="Randomize questions" />
          <Toggle name="randomize_options" checked={exam.randomize_options} onChange={onChange} label="Randomize options" />
          <Toggle name="show_results_immediately" checked={exam.show_results_immediately} onChange={onChange} label="Show objective score immediately" />
          <Toggle name="allow_retake" checked={exam.allow_retake} onChange={onChange} label="Allow retake" />
          <Toggle name="enable_proctoring" checked={exam.enable_proctoring} onChange={onChange} label="Enable proctoring" />
        </div>
      </div>

      {!isNew && (
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-900">Questions ({questions.length})</h2>
            <button
              onClick={() => setEditingQuestion({ exam: exam.id, subject: exam.subject, question_type: 'single_choice', text: '', marks: 1, negative_marks: 0, options: [{ text: '', is_correct: true, order: 0 }, { text: '', is_correct: false, order: 1 }], test_cases: [] })}
              className="btn-primary"
            >
              <Plus className="h-4 w-4" /> Add question
            </button>
          </div>
          {questions.length === 0 ? (
            <p className="text-slate-500">No questions yet. Add some to make this exam attemptable.</p>
          ) : (
            <ul className="divide-y divide-slate-100">
              {questions.map((q, i) => (
                <li key={q.id} className="py-3 flex items-start justify-between">
                  <div className="flex-1 pr-3">
                    <p className="text-xs uppercase tracking-wide text-slate-500 font-semibold">
                      Q{i + 1} • {q.question_type.replace('_', ' ')} • {q.marks} marks • {q.difficulty}
                    </p>
                    <p className="font-medium text-slate-900 mt-1 line-clamp-2">{q.text}</p>
                  </div>
                  <div className="flex gap-1">
                    <button onClick={() => setEditingQuestion(q)} className="btn-ghost p-2"><Edit2 className="h-4 w-4" /></button>
                    <button onClick={() => removeQuestion(q.id)} className="btn-ghost p-2 text-red-600 hover:bg-red-50"><Trash2 className="h-4 w-4" /></button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {editingQuestion && (
        <QuestionModal
          question={editingQuestion}
          exam={exam}
          onClose={() => setEditingQuestion(null)}
          onSaved={() => { setEditingQuestion(null); reloadQuestions(); }}
        />
      )}

      {enrollOpen && (
        <EnrollModal
          slug={slug}
          onClose={() => setEnrollOpen(false)}
        />
      )}
    </div>
  );
}

function Toggle({ name, checked, onChange, label }) {
  return (
    <label className="flex items-center gap-2 cursor-pointer">
      <input type="checkbox" name={name} checked={!!checked} onChange={onChange} className="h-4 w-4 rounded text-primary-600" />
      <span className="text-slate-700">{label}</span>
    </label>
  );
}

function buildQuestionPayload(form, exam) {
  const payload = {
    text: form.text,
    question_type: form.question_type,
    marks: form.marks,
    negative_marks: form.negative_marks,
    difficulty: form.difficulty,
    order: form.order,
    is_in_bank: form.is_in_bank,
    exam: exam.id,
    subject: exam.subject,
    correct_answer_text: '',
    coding_language: '',
    starter_code: '',
    expected_output: '',
    options: [],
    test_cases: [],
  };

  if (form.question_type === 'fill_blank') {
    payload.correct_answer_text = form.correct_answer_text || '';
  } else if (form.question_type === 'coding') {
    payload.coding_language = form.coding_language || 'python';
    payload.starter_code = form.starter_code || '';
    payload.expected_output = form.expected_output || '';
    payload.test_cases = (form.test_cases || []).map((t, i) => ({
      input_data: t.input_data ?? '',
      expected_output: String(t.expected_output ?? '').trim(),
      is_hidden: !!t.is_hidden,
      weight: Number(t.weight) || 1,
      order: t.order ?? i,
    }));
  } else if (
    form.question_type === 'single_choice'
    || form.question_type === 'multiple_choice'
    || form.question_type === 'true_false'
  ) {
    payload.options = (form.options || []).map((o, i) => ({
      text: o.text,
      is_correct: !!o.is_correct,
      order: o.order ?? i,
    }));
  }

  return payload;
}

function applyQuestionTypeChange(prev, newType) {
  const next = { ...prev, question_type: newType };
  if (newType === 'coding') {
    next.options = [];
    if (!next.test_cases?.length) next.test_cases = [];
  } else if (newType === 'descriptive' || newType === 'fill_blank') {
    next.options = [];
    next.test_cases = [];
  } else if (newType === 'true_false') {
    next.test_cases = [];
    next.options = [
      { text: 'True', is_correct: true, order: 0 },
      { text: 'False', is_correct: false, order: 1 },
    ];
  } else if (newType === 'single_choice' || newType === 'multiple_choice') {
    next.test_cases = [];
    if (!next.options?.length) {
      next.options = [
        { text: '', is_correct: true, order: 0 },
        { text: '', is_correct: false, order: 1 },
      ];
    }
  }
  return next;
}

function QuestionModal({ question, exam, onClose, onSaved }) {
  const [form, setForm] = useState({
    text: question.text || '',
    question_type: question.question_type,
    marks: question.marks || 1,
    negative_marks: question.negative_marks || 0,
    difficulty: question.difficulty || 'medium',
    correct_answer_text: question.correct_answer_text || '',
    coding_language: question.coding_language || 'python',
    starter_code: question.starter_code || '',
    expected_output: question.expected_output || '',
    options: question.question_type === 'coding' ? [] : (question.options || []),
    test_cases: question.test_cases || [],
    order: question.order || 0,
    is_in_bank: question.is_in_bank ?? true,
  });
  const [saving, setSaving] = useState(false);

  const save = async () => {
    if (!form.text?.trim()) {
      toast.error('Question text is required');
      return;
    }
    if (form.question_type === 'coding') {
      const cases = form.test_cases || [];
      if (!cases.length) {
        toast.error('Add at least one test case for coding questions');
        return;
      }
      const bad = cases.findIndex((t) => !String(t.expected_output ?? '').trim());
      if (bad >= 0) {
        toast.error(`Test case #${bad + 1}: expected output is required`);
        return;
      }
    }

    setSaving(true);
    try {
      const payload = buildQuestionPayload(form, exam);
      if (question.id) {
        await questionsApi.update(question.id, payload);
      } else {
        await questionsApi.create(payload);
      }
      toast.success('Question saved');
      onSaved();
    } catch (err) {
      toast.error(formatApiError(err, 'Could not save question'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal
      open
      onClose={onClose}
      title={question.id ? 'Edit question' : 'New question'}
      size="lg"
      footer={(
        <>
          <button onClick={onClose} className="btn-secondary">Cancel</button>
          <button onClick={save} disabled={saving} className="btn-primary"><Save className="h-4 w-4" /> Save</button>
        </>
      )}
    >
      <div className="grid gap-4 md:grid-cols-2">
        <div className="md:col-span-2">
          <label className="label">Question text</label>
          <textarea rows={3} className="input" value={form.text} onChange={(e) => setForm({ ...form, text: e.target.value })} />
        </div>
        <div>
          <label className="label">Type</label>
          <select
            className="input"
            value={form.question_type}
            onChange={(e) => setForm((prev) => applyQuestionTypeChange(prev, e.target.value))}
          >
            {QUESTION_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
          </select>
        </div>
        <div>
          <label className="label">Difficulty</label>
          <select className="input" value={form.difficulty} onChange={(e) => setForm({ ...form, difficulty: e.target.value })}>
            {DIFFICULTY.map((d) => <option key={d} value={d} className="capitalize">{d}</option>)}
          </select>
        </div>
        <div>
          <label className="label">Marks</label>
          <input type="number" step="0.5" className="input" value={form.marks} onChange={(e) => setForm({ ...form, marks: e.target.value })} />
        </div>
        <div>
          <label className="label">Negative marks</label>
          <input type="number" step="0.25" className="input" value={form.negative_marks} onChange={(e) => setForm({ ...form, negative_marks: e.target.value })} />
        </div>

        {(form.question_type === 'single_choice' || form.question_type === 'multiple_choice' || form.question_type === 'true_false') && (
          <OptionsEditor form={form} setForm={setForm} />
        )}

        {form.question_type === 'fill_blank' && (
          <div className="md:col-span-2">
            <label className="label">Correct answer (text)</label>
            <input className="input" value={form.correct_answer_text} onChange={(e) => setForm({ ...form, correct_answer_text: e.target.value })} />
          </div>
        )}

        {form.question_type === 'coding' && (
          <CodingEditor form={form} setForm={setForm} />
        )}
      </div>
    </Modal>
  );
}

function OptionsEditor({ form, setForm }) {
  const isSingle = form.question_type !== 'multiple_choice';
  const setOpt = (idx, patch) => {
    const opts = form.options.map((o, i) => (i === idx ? { ...o, ...patch } : o));
    if (isSingle && patch.is_correct === true) {
      for (let i = 0; i < opts.length; i++) if (i !== idx) opts[i].is_correct = false;
    }
    setForm({ ...form, options: opts });
  };
  const add = () => setForm({ ...form, options: [...form.options, { text: '', is_correct: false, order: form.options.length }] });
  const del = (idx) => setForm({ ...form, options: form.options.filter((_, i) => i !== idx) });

  if (form.question_type === 'true_false' && form.options.length === 0) {
    setForm({ ...form, options: [{ text: 'True', is_correct: true, order: 0 }, { text: 'False', is_correct: false, order: 1 }] });
  }

  return (
    <div className="md:col-span-2">
      <label className="label">Options</label>
      <ul className="space-y-2">
        {form.options.map((o, i) => (
          <li key={i} className="flex items-center gap-2">
            <input type={isSingle ? 'radio' : 'checkbox'} checked={o.is_correct} onChange={(e) => setOpt(i, { is_correct: e.target.checked })} />
            <input className="input flex-1" value={o.text} onChange={(e) => setOpt(i, { text: e.target.value })} placeholder={`Option ${i + 1}`} />
            <button onClick={() => del(i)} className="btn-ghost p-2 text-red-600"><Trash2 className="h-4 w-4" /></button>
          </li>
        ))}
      </ul>
      <button onClick={add} className="btn-secondary mt-2"><Plus className="h-4 w-4" /> Add option</button>
    </div>
  );
}

function CodingEditor({ form, setForm }) {
  const updateTC = (idx, patch) => {
    setForm({
      ...form,
      test_cases: form.test_cases.map((t, i) => (i === idx ? { ...t, ...patch } : t)),
    });
  };
  const addTC = () => setForm({
    ...form,
    test_cases: [...form.test_cases, { input_data: '', expected_output: '', is_hidden: false, weight: 1, order: form.test_cases.length }],
  });
  const delTC = (idx) => setForm({ ...form, test_cases: form.test_cases.filter((_, i) => i !== idx) });

  return (
    <>
      <div>
        <label className="label">Language</label>
        <select className="input" value={form.coding_language} onChange={(e) => setForm({ ...form, coding_language: e.target.value })}>
          {CODING_LANGUAGES.map((l) => (
            <option key={l.value} value={l.value}>{l.label}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="label">Expected output (reference)</label>
        <input className="input" value={form.expected_output} onChange={(e) => setForm({ ...form, expected_output: e.target.value })} />
      </div>
      <div className="md:col-span-2">
        <label className="label">Starter code</label>
        <CodeStudioEditor
          language={monacoLanguageFor(form.coding_language || 'python')}
          value={form.starter_code}
          onChange={(v) => setForm({ ...form, starter_code: v })}
          height="220px"
        />
      </div>
      <div className="md:col-span-2">
        <label className="label">Test cases</label>
        <ul className="space-y-2">
          {form.test_cases.map((t, i) => (
            <li key={i} className="grid grid-cols-12 gap-2 items-start">
              <input className="input col-span-4" value={t.input_data} onChange={(e) => updateTC(i, { input_data: e.target.value })} placeholder={`Input #${i + 1}`} />
              <input className="input col-span-4" value={t.expected_output} onChange={(e) => updateTC(i, { expected_output: e.target.value })} placeholder="Expected output" />
              <label className="col-span-2 flex items-center gap-1 text-sm text-slate-600">
                <input type="checkbox" checked={t.is_hidden} onChange={(e) => updateTC(i, { is_hidden: e.target.checked })} />
                Hidden
              </label>
              <input type="number" className="input col-span-1" value={t.weight} onChange={(e) => updateTC(i, { weight: e.target.value })} />
              <button onClick={() => delTC(i)} className="btn-ghost p-2 text-red-600 col-span-1"><Trash2 className="h-4 w-4" /></button>
            </li>
          ))}
        </ul>
        <button onClick={addTC} className="btn-secondary mt-2"><Plus className="h-4 w-4" /> Add test case</button>
      </div>
    </>
  );
}

function EnrollModal({ slug, onClose }) {
  const [students, setStudents] = useState([]);
  const [selected, setSelected] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(false);

  useEffect(() => {
    usersApi
      .list({ role: 'student', is_active: true, page_size: 100 })
      .then((r) => setStudents(r.data?.results || []))
      .finally(() => setLoading(false));
  }, []);

  const toggle = (id) => {
    const next = new Set(selected);
    if (next.has(id)) next.delete(id); else next.add(id);
    setSelected(next);
  };

  const enroll = async () => {
    if (selected.size === 0) return;
    setEnrolling(true);
    try {
      await examsApi.enroll(slug, Array.from(selected));
      toast.success(`Enrolled ${selected.size} student(s)`);
      onClose();
    } catch {
      toast.error('Could not enroll');
    } finally {
      setEnrolling(false);
    }
  };

  const enrollAll = async () => {
    setEnrolling(true);
    try {
      await examsApi.enrollAll(slug);
      toast.success('All students enrolled');
      onClose();
    } catch {
      toast.error('Could not enroll all');
    } finally {
      setEnrolling(false);
    }
  };

  return (
    <Modal
      open
      onClose={onClose}
      title="Enroll students"
      size="lg"
      footer={(
        <>
          <button className="btn-secondary mr-auto" onClick={enrollAll} disabled={enrolling}>Enroll all active students</button>
          <button onClick={onClose} className="btn-secondary">Cancel</button>
          <button onClick={enroll} disabled={enrolling || selected.size === 0} className="btn-primary">Enroll selected ({selected.size})</button>
        </>
      )}
    >
      {loading ? <Spinner /> : (
        <ul className="space-y-2 max-h-[60vh] overflow-y-auto">
          {students.map((s) => (
            <li key={s.id}>
              <label className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-50 cursor-pointer">
                <input type="checkbox" checked={selected.has(s.id)} onChange={() => toggle(s.id)} className="h-4 w-4 rounded text-primary-600" />
                <div>
                  <p className="font-medium text-slate-900">{s.full_name}</p>
                  <p className="text-xs text-slate-500">{s.email}</p>
                </div>
              </label>
            </li>
          ))}
        </ul>
      )}
    </Modal>
  );
}

function toLocalInput(d) {
  if (!d) return '';
  const date = new Date(d);
  if (Number.isNaN(date.getTime())) return d;
  const pad = (n) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}
