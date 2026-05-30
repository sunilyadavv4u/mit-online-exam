import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { FileQuestion, Loader2, Sparkles, Copy, Download, Upload, ClipboardList } from 'lucide-react';
import { aiApi, examsApi } from '../../api/endpoints';
import { formatApiError } from '../../utils/helpers';

function countPaperQuestions(paper) {
  if (!paper || paper.format === 'markdown') return 0;
  return (paper.sections || []).reduce(
    (n, s) => n + (s.questions || []).filter((q) => q.text).length,
    0,
  );
}

const DIFFICULTY = ['easy', 'medium', 'hard'];

const ACCEPT_NOTES = '.pdf,.txt,.text,.py,.md,.markdown,.sql,.json';
const MAX_FILE_MB = 100;

const TYPE_OPTIONS = [
  { value: 'single_choice', label: 'Single MCQ' },
  { value: 'multiple_choice', label: 'Multi MCQ' },
  { value: 'true_false', label: 'True / False' },
  { value: 'fill_blank', label: 'Fill blank' },
  { value: 'descriptive', label: 'Descriptive' },
  { value: 'coding', label: 'Coding' },
];

export default function TeacherQuestionPaperPage() {
  const [prompt, setPrompt] = useState(
    'Create a balanced question paper with MCQs, 2 descriptive, and 1 coding question based on my notes.',
  );
  const [notes, setNotes] = useState('');
  const [subject, setSubject] = useState('');
  const [totalMarks, setTotalMarks] = useState(100);
  const [duration, setDuration] = useState(60);
  const [numQuestions, setNumQuestions] = useState(10);
  const [difficulty, setDifficulty] = useState('medium');
  const [types, setTypes] = useState(['single_choice', 'fill_blank', 'descriptive', 'coding']);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadedName, setUploadedName] = useState('');
  const [notesMode, setNotesMode] = useState('replace');
  const fileInputRef = useRef(null);
  const [paper, setPaper] = useState(null);
  const [raw, setRaw] = useState('');
  const [exams, setExams] = useState([]);
  const [examsLoading, setExamsLoading] = useState(false);
  const [selectedExamId, setSelectedExamId] = useState('');
  const [setLive, setSetLive] = useState(false);
  const [importing, setImporting] = useState(false);
  const [lastImport, setLastImport] = useState(null);

  const isMarkdown = paper?.format === 'markdown';
  const questionCount = countPaperQuestions(paper);
  const canImport = paper && !isMarkdown && questionCount > 0;

  useEffect(() => {
    if (!canImport) return;
    setExamsLoading(true);
    examsApi
      .list({ page_size: 100 })
      .then((r) => {
        const list = r.data?.results || [];
        setExams(list);
        if (!selectedExamId && list.length) {
          const draft = list.find((e) => e.status === 'draft') || list[0];
          setSelectedExamId(draft.id);
        }
      })
      .catch(() => toast.error('Could not load exams'))
      .finally(() => setExamsLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canImport, paper]);

  const toggleType = (value) => {
    setTypes((prev) => (
      prev.includes(value) ? prev.filter((t) => t !== value) : [...prev, value]
    ));
  };

  const generate = async () => {
    if (!prompt.trim()) {
      toast.error('Add a prompt describing what you need in the paper');
      return;
    }
    if (!notes.trim()) {
      toast.error('Paste teaching notes or upload a PDF / text / .py file');
      return;
    }
    if (!types.length) {
      toast.error('Select at least one question type');
      return;
    }

    setLoading(true);
    setPaper(null);
    setRaw('');
    try {
      const r = await aiApi.generateQuestionPaper({
        prompt: prompt.trim(),
        teaching_notes: notes.trim(),
        subject: subject.trim(),
        total_marks: Number(totalMarks),
        duration_minutes: Number(duration),
        num_questions: Number(numQuestions),
        difficulty,
        question_types: types,
      });
      setPaper(r.data?.question_paper || null);
      setRaw(r.data?.raw_response || '');
      toast.success('Question paper generated');
    } catch (err) {
      toast.error(formatApiError(err, 'Could not generate question paper'));
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) return;

    if (file.size > MAX_FILE_MB * 1024 * 1024) {
      toast.error(`File must be under ${MAX_FILE_MB} MB`);
      return;
    }

    const ext = file.name.includes('.') ? file.name.slice(file.name.lastIndexOf('.')).toLowerCase() : '';
    const allowed = ACCEPT_NOTES.split(',');
    if (!allowed.includes(ext)) {
      toast.error('Use PDF, TXT, PY, MD, SQL, or JSON');
      return;
    }

    setUploading(true);
    try {
      const r = await aiApi.extractNotesFile(file);
      const text = r.data?.text || '';
      setNotes((prev) => (
        notesMode === 'append' && prev.trim()
          ? `${prev.trim()}\n\n--- ${r.data?.filename || file.name} ---\n\n${text}`
          : text
      ));
      setUploadedName(r.data?.filename || file.name);
      toast.success(`Loaded ${r.data?.char_count?.toLocaleString() || text.length} characters from file`);
    } catch (err) {
      toast.error(formatApiError(err, 'Could not read file'));
    } finally {
      setUploading(false);
    }
  };

  const copyAll = () => {
    const text = raw || JSON.stringify(paper, null, 2);
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const downloadJson = () => {
    const blob = new Blob([JSON.stringify(paper || { raw }, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'question-paper.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const importToExam = async () => {
    if (!selectedExamId) {
      toast.error('Select an exam');
      return;
    }
    setImporting(true);
    try {
      const r = await aiApi.importToExam({
        exam_id: selectedExamId,
        question_paper: paper,
        set_live: setLive,
        update_exam_metadata: true,
      });
      setLastImport(r.data);
      toast.success(`Added ${r.data.created_count} questions to "${r.data.exam_title}"`);
    } catch (err) {
      toast.error(formatApiError(err, 'Import failed'));
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-5xl">
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-violet-500 to-primary-600 text-white flex items-center justify-center">
          <FileQuestion className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">AI Question Paper Generator</h1>
          <p className="text-slate-600 text-sm">
            For teachers — paste your notes and instructions; Databricks Llama-4 Maverick drafts a paper.
          </p>
        </div>
      </div>

      <div className="card p-6 space-y-4">
        <div>
          <label className="label">Your prompt / requirements</label>
          <textarea
            rows={3}
            className="input"
            placeholder="e.g. 15 MCQs from chapter 3, 2 short answers, medium difficulty, no trick questions"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
          />
        </div>

        <div>
          <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
            <label className="label mb-0">Teaching notes</label>
            <span className="text-xs text-slate-500">
              {notes.length > 0 ? `${notes.length.toLocaleString()} characters` : 'Paste or upload'}
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-3 mb-2 p-3 rounded-lg border border-dashed border-slate-300 bg-slate-50">
            <input
              ref={fileInputRef}
              type="file"
              accept={ACCEPT_NOTES}
              className="hidden"
              onChange={handleFileUpload}
            />
            <button
              type="button"
              disabled={uploading}
              onClick={() => fileInputRef.current?.click()}
              className="btn-secondary py-1.5"
            >
              {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
              {uploading ? 'Reading file...' : 'Upload notes file'}
            </button>
            <span className="text-xs text-slate-600">PDF, TXT, PY, MD, SQL (max {MAX_FILE_MB} MB)</span>
            <label className="inline-flex items-center gap-2 text-xs text-slate-600 ml-auto">
              <span>On upload:</span>
              <select
                className="input py-1 text-xs max-w-[140px]"
                value={notesMode}
                onChange={(e) => setNotesMode(e.target.value)}
              >
                <option value="replace">Replace notes</option>
                <option value="append">Append to notes</option>
              </select>
            </label>
          </div>
          {uploadedName && (
            <p className="text-xs text-emerald-700 mb-2">Last uploaded: {uploadedName}</p>
          )}

          <textarea
            rows={10}
            className="input font-mono text-sm"
            placeholder="Paste lecture notes here, or use Upload to load a PDF / .txt / .py file..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div>
            <label className="label">Subject (optional)</label>
            <input className="input" value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="Python" />
          </div>
          <div>
            <label className="label">Total marks</label>
            <input type="number" className="input" value={totalMarks} onChange={(e) => setTotalMarks(e.target.value)} />
          </div>
          <div>
            <label className="label">Duration (min)</label>
            <input type="number" className="input" value={duration} onChange={(e) => setDuration(e.target.value)} />
          </div>
          <div>
            <label className="label"># Questions (approx)</label>
            <input type="number" className="input" value={numQuestions} onChange={(e) => setNumQuestions(e.target.value)} />
          </div>
        </div>

        <div>
          <label className="label">Difficulty</label>
          <select className="input max-w-xs" value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
            {DIFFICULTY.map((d) => (
              <option key={d} value={d} className="capitalize">{d}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="label">Question types to include</label>
          <div className="flex flex-wrap gap-2 mt-1">
            {TYPE_OPTIONS.map((t) => (
              <label
                key={t.value}
                className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm cursor-pointer ${
                  types.includes(t.value)
                    ? 'border-primary-500 bg-primary-50 text-primary-800'
                    : 'border-slate-200 text-slate-600'
                }`}
              >
                <input
                  type="checkbox"
                  className="sr-only"
                  checked={types.includes(t.value)}
                  onChange={() => toggleType(t.value)}
                />
                {t.label}
              </label>
            ))}
          </div>
        </div>

        <button onClick={generate} disabled={loading} className="btn-primary">
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
          {loading ? 'Generating...' : 'Generate question paper'}
        </button>
      </div>

      {paper && (
        <div className="card p-6 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-lg font-semibold text-slate-900">
              {paper.title || 'Generated paper'}
            </h2>
            <div className="flex gap-2">
              <button type="button" onClick={copyAll} className="btn-secondary py-1.5">
                <Copy className="h-4 w-4" /> Copy
              </button>
              <button type="button" onClick={downloadJson} className="btn-secondary py-1.5">
                <Download className="h-4 w-4" /> JSON
              </button>
            </div>
          </div>

          {isMarkdown ? (
            <pre className="whitespace-pre-wrap text-sm text-slate-800 bg-slate-50 p-4 rounded-lg border border-slate-200">
              {paper.content}
            </pre>
          ) : (
            <>
              {paper.instructions && (
                <p className="text-sm text-slate-600 border-l-4 border-primary-400 pl-3">{paper.instructions}</p>
              )}
              <p className="text-xs text-slate-500">
                {paper.subject && <>Subject: {paper.subject} · </>}
                Marks: {paper.total_marks ?? totalMarks} · Duration: {paper.duration_minutes ?? duration} min
              </p>
              {(paper.sections || []).map((section, si) => (
                <div key={si} className="border-t border-slate-100 pt-4">
                  <h3 className="font-semibold text-slate-800">{section.name || `Section ${si + 1}`}</h3>
                  <ol className="mt-3 space-y-4 list-decimal list-inside">
                    {(section.questions || []).map((q, qi) => (
                      <li key={qi} className="text-slate-800">
                        <span className="font-medium">{q.text}</span>
                        <span className="text-xs text-slate-500 ml-2">
                          ({q.type?.replace('_', ' ')}, {q.marks} marks, {q.difficulty || difficulty})
                        </span>
                        {q.options?.length > 0 && (
                          <ul className="list-disc list-inside ml-4 mt-1 text-sm text-slate-600">
                            {q.options.map((opt, oi) => (
                              <li key={oi}>{typeof opt === 'string' ? opt : opt.text || JSON.stringify(opt)}</li>
                            ))}
                          </ul>
                        )}
                        {q.correct_answer && (
                          <p className="text-xs text-emerald-700 mt-1">Answer: {Array.isArray(q.correct_answer) ? q.correct_answer.join(', ') : q.correct_answer}</p>
                        )}
                        {q.starter_code && (
                          <pre className="mt-1 text-xs bg-slate-900 text-slate-100 p-2 rounded overflow-x-auto">{q.starter_code}</pre>
                        )}
                      </li>
                    ))}
                  </ol>
                </div>
              ))}
            </>
          )}

          {canImport && (
            <div className="mt-6 p-4 rounded-xl border-2 border-primary-200 bg-primary-50/50 space-y-4">
              <div className="flex items-center gap-2">
                <ClipboardList className="h-5 w-5 text-primary-600" />
                <h3 className="font-semibold text-slate-900">Add to exam</h3>
              </div>
              <p className="text-sm text-slate-600">
                Import all <strong>{questionCount}</strong> questions into an exam. You can set it live immediately or keep it as draft.
              </p>

              <div className="grid gap-3 md:grid-cols-2">
                <div>
                  <label className="label">Choose exam</label>
                  {examsLoading ? (
                    <p className="text-sm text-slate-500">Loading exams...</p>
                  ) : exams.length === 0 ? (
                    <p className="text-sm text-slate-600">
                      No exams yet.{' '}
                      <Link to="/exams/new" className="text-primary-600 font-medium hover:underline">
                        Create an exam first
                      </Link>
                    </p>
                  ) : (
                    <select
                      className="input"
                      value={selectedExamId}
                      onChange={(e) => setSelectedExamId(e.target.value)}
                    >
                      {exams.map((ex) => (
                        <option key={ex.id} value={ex.id}>
                          {ex.title} ({ex.status}) — {ex.question_count ?? 0} existing Qs
                        </option>
                      ))}
                    </select>
                  )}
                </div>
                <div className="flex items-end">
                  <label className="flex items-center gap-2 cursor-pointer text-sm text-slate-700">
                    <input
                      type="checkbox"
                      checked={setLive}
                      onChange={(e) => setSetLive(e.target.checked)}
                      className="h-4 w-4 rounded text-primary-600"
                    />
                    Set exam to <strong>Live</strong> after import
                  </label>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={importToExam}
                  disabled={importing || !selectedExamId || exams.length === 0}
                  className="btn-primary"
                >
                  {importing ? <Loader2 className="h-4 w-4 animate-spin" /> : <ClipboardList className="h-4 w-4" />}
                  {importing ? 'Importing...' : 'Add questions to exam'}
                </button>
                {lastImport?.exam_slug && (
                  <Link
                    to={`/exams/${lastImport.exam_slug}/edit`}
                    className="btn-secondary"
                  >
                    Open exam editor
                  </Link>
                )}
              </div>

              {lastImport && (
                <p className="text-xs text-emerald-800">
                  Imported {lastImport.created_count} questions · status: {lastImport.exam_status}
                </p>
              )}
            </div>
          )}

          {isMarkdown && (
            <p className="text-xs text-amber-700">
              This output is plain text only. Regenerate the paper to import questions automatically.
            </p>
          )}

          {!canImport && !isMarkdown && paper && (
            <p className="text-xs text-slate-500">No structured questions to import.</p>
          )}
        </div>
      )}
    </div>
  );
}
