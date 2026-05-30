import { useState } from 'react';
import { Link } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import toast from 'react-hot-toast';
import {
  Code2,
  Copy,
  Loader2,
  Play,
  RotateCcw,
  Sparkles,
} from 'lucide-react';
import {
  CODE_STUDIO_LANGUAGES,
  CODE_STUDIO_TEMPLATES,
  monacoLanguageFor,
} from '../../constants/codeStudioLanguages';
import { codeStudioApi } from '../../api/endpoints';
import { formatApiError } from '../../utils/helpers';

export default function CodeStudioPage() {
  const [langId, setLangId] = useState('python');
  const [code, setCode] = useState(CODE_STUDIO_TEMPLATES.python);
  const [stdin, setStdin] = useState('');
  const [expected, setExpected] = useState('');
  const [output, setOutput] = useState(null);
  const [running, setRunning] = useState(false);

  const lang = CODE_STUDIO_LANGUAGES.find((l) => l.id === langId) || CODE_STUDIO_LANGUAGES[0];

  const switchLanguage = (id) => {
    setLangId(id);
    setCode(CODE_STUDIO_TEMPLATES[id] || '');
    setOutput(null);
  };

  const resetTemplate = () => {
    setCode(CODE_STUDIO_TEMPLATES[langId] || '');
    setOutput(null);
    toast.success('Template restored');
  };

  const copyCode = () => {
    navigator.clipboard.writeText(code);
    toast.success('Code copied');
  };

  const run = async () => {
    setRunning(true);
    setOutput(null);
    try {
      const r = await codeStudioApi.run({
        code,
        language: langId,
        stdin,
        expected_output: expected,
      });
      setOutput(r.data);
    } catch (err) {
      toast.error(formatApiError(err, 'Run failed'));
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-slate-800 to-primary-700 text-white flex items-center justify-center">
            <Code2 className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">MIT Code Studio</h1>
            <p className="text-sm text-slate-600">
              In-browser editor for Python, SQL Server, PySpark, and Java
            </p>
          </div>
        </div>
        <Link to="/ai-assistant" className="btn-secondary text-sm">
          <Sparkles className="h-4 w-4" /> AI Code Assistant
        </Link>
      </div>

      <div className="flex flex-wrap gap-2">
        {CODE_STUDIO_LANGUAGES.map((l) => (
          <button
            key={l.id}
            type="button"
            onClick={() => switchLanguage(l.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium border transition ${
              langId === l.id
                ? 'border-primary-500 bg-primary-50 text-primary-800'
                : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
            }`}
          >
            {l.label}
          </button>
        ))}
      </div>

      <p className="text-sm text-slate-600">{lang.description}</p>

      <div className="card p-0 overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 border-b border-slate-200 bg-slate-50">
          <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            {lang.label} · Monaco Editor
          </span>
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={resetTemplate} className="btn-secondary py-1.5 text-xs">
              <RotateCcw className="h-3.5 w-3.5" /> Reset
            </button>
            <button type="button" onClick={copyCode} className="btn-secondary py-1.5 text-xs">
              <Copy className="h-3.5 w-3.5" /> Copy
            </button>
            <button
              type="button"
              onClick={run}
              disabled={running || !lang.canRun}
              className="btn-primary py-1.5 text-xs"
            >
              {running ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
              {running ? 'Running...' : `Run ${lang.label}`}
            </button>
          </div>
        </div>

        <Editor
          height="440px"
          theme="vs-dark"
          language={monacoLanguageFor(langId)}
          value={code}
          onChange={(v) => setCode(v ?? '')}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            scrollBeyondLastLine: false,
            tabSize: langId === 'sql' ? 2 : 4,
            wordWrap: 'on',
            automaticLayout: true,
          }}
        />
      </div>

      {langId === 'python' && (
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="label">Standard input (optional)</label>
            <textarea
              rows={3}
              className="input font-mono text-sm"
              placeholder="Input passed to your Python program"
              value={stdin}
              onChange={(e) => setStdin(e.target.value)}
            />
          </div>
          <div>
            <label className="label">Expected output (optional — runs as one test)</label>
            <textarea
              rows={3}
              className="input font-mono text-sm"
              placeholder="If set, stdout must match exactly"
              value={expected}
              onChange={(e) => setExpected(e.target.value)}
            />
          </div>
        </div>
      )}

      {output && (
        <div className="card p-4 bg-slate-900 text-slate-100 font-mono text-sm space-y-2 max-h-72 overflow-auto">
          <p className="text-primary-300 font-semibold text-xs uppercase tracking-wide">Output</p>
          {output.mode === 'editor_only' && (
            <p className="text-amber-300">{output.message}</p>
          )}
          {output.mode === 'freeform' && (
            <>
              {output.runtime && (
                <p className="text-slate-400 text-xs">Runtime: {output.runtime}</p>
              )}
              {output.stdout && (
                <pre className="text-emerald-300 whitespace-pre-wrap">{output.stdout}</pre>
              )}
              {output.stderr && (
                <pre className="text-red-300 whitespace-pre-wrap">{output.stderr}</pre>
              )}
              {output.exit_code !== undefined && (
                <p className="text-slate-400 text-xs">Exit code: {output.exit_code}</p>
              )}
            </>
          )}
          {output.mode === 'test' && (
            <>
              <p className="text-emerald-400">
                Passed {output.passed} / {output.total}
              </p>
              {(output.details || []).map((d, i) => (
                <div key={i} className="border-t border-slate-700 pt-2">
                  <p>{d.passed ? '✓' : '✗'} expected: {d.expected}</p>
                  <p className="text-slate-400">actual: {d.actual || '(empty)'}</p>
                  {d.stderr && <p className="text-red-300">{d.stderr}</p>}
                </div>
              ))}
            </>
          )}
        </div>
      )}

      <p className="text-xs text-slate-500">
        <strong>Java:</strong> needs JDK on the server. <strong>PySpark:</strong> needs Java + <code>pip install pyspark</code>.
        <strong> SQL:</strong> uses in-memory SQLite with a demo <code>Employee</code> table (TOP/dbo. normalized);
        for real SQL Server set <code>CODE_STUDIO_MSSQL_CONNECTION</code> in backend <code>.env</code>.
        Use <Link to="/mit-chat" className="text-primary-600 hover:underline">MIT AI Chat</Link>
        {' '}or <Link to="/ai-assistant" className="text-primary-600 hover:underline">AI Code Assistant</Link>
        {' '}for convert/explain help.
      </p>
    </div>
  );
}
