import { useState } from 'react';
import Editor from '@monaco-editor/react';
import toast from 'react-hot-toast';
import { Sparkles, Copy, Code2, Wand2, Loader2 } from 'lucide-react';
import { aiApi } from '../../api/endpoints';

const TASKS = [
  { id: 'sql_to_spark_sql', label: 'SQL → Databricks Spark SQL', api: aiApi.sqlToSparkSql, lang: 'sql', help: 'Wrap your SQL into spark.sql(""" ... """) the same way Databricks notebooks expect.' },
  { id: 'sql_to_pyspark', label: 'SQL → PySpark DataFrame API', api: aiApi.sqlToPySpark, lang: 'sql', help: 'Convert SELECT/WHERE/JOIN logic into the equivalent PySpark code.' },
  { id: 'python_to_pyspark', label: 'Python (pandas) → PySpark', api: aiApi.pythonToPySpark, lang: 'python', help: 'Translate vanilla pandas / Python data wrangling to PySpark.' },
  { id: 'explain', label: 'Explain code (English)', api: (code) => aiApi.explain(code, 'python'), lang: 'python', help: 'Get a beginner-friendly explanation of the highlighted code.' },
];

export default function AIAssistantPage() {
  const [taskId, setTaskId] = useState(TASKS[0].id);
  const [input, setInput] = useState(EXAMPLE);
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);

  const task = TASKS.find((t) => t.id === taskId);

  const run = async () => {
    setLoading(true);
    try {
      const r = await task.api(input);
      setOutput(r.data?.response || '');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'AI request failed - is Databricks configured?');
    } finally {
      setLoading(false);
    }
  };

  const copy = () => {
    navigator.clipboard.writeText(output);
    toast.success('Copied');
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-fuchsia-500 to-primary-600 text-white flex items-center justify-center">
          <Sparkles className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">AI Code Assistant</h1>
          <p className="text-slate-600 text-sm">Powered by <strong>Databricks Llama-4 Maverick</strong>.</p>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-4">
        {TASKS.map((t) => (
          <button
            key={t.id}
            onClick={() => { setTaskId(t.id); setOutput(''); }}
            className={`card p-4 text-left transition ${taskId === t.id ? 'ring-2 ring-primary-500' : 'hover:shadow-md'}`}
          >
            <Code2 className="h-5 w-5 text-primary-600" />
            <p className="mt-2 font-semibold text-slate-900 text-sm">{t.label}</p>
            <p className="text-xs text-slate-500 mt-1">{t.help}</p>
          </button>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card p-0 overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
            <p className="text-sm font-semibold text-slate-700">Input ({task.lang})</p>
            <button onClick={run} disabled={loading} className="btn-primary py-1.5 px-3">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Wand2 className="h-4 w-4" />}
              {loading ? 'Running...' : 'Convert'}
            </button>
          </div>
          <Editor
            height="400px"
            theme="vs-dark"
            language={task.lang}
            value={input}
            onChange={(v) => setInput(v ?? '')}
            options={{ fontSize: 13, minimap: { enabled: false } }}
          />
        </div>
        <div className="card p-0 overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
            <p className="text-sm font-semibold text-slate-700">Output</p>
            <button onClick={copy} disabled={!output} className="btn-ghost py-1.5 px-3">
              <Copy className="h-4 w-4" /> Copy
            </button>
          </div>
          <Editor
            height="400px"
            theme="vs-dark"
            language={taskId === 'explain' ? 'markdown' : 'python'}
            value={output}
            options={{ readOnly: true, fontSize: 13, minimap: { enabled: false }, wordWrap: 'on' }}
          />
        </div>
      </div>
    </div>
  );
}

const EXAMPLE = `-- Try the assistant!
SELECT TOP 100
  emp_id, first_name, last_name, dept, salary
FROM employees
WHERE dept = 'Data Engineering'
ORDER BY salary DESC;
`;
