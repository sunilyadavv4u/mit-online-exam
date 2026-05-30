import Editor from '@monaco-editor/react';

const DEFAULT_OPTIONS = {
  minimap: { enabled: false },
  fontSize: 14,
  scrollBeyondLastLine: false,
  tabSize: 4,
  wordWrap: 'on',
  automaticLayout: true,
};

/**
 * Monaco code editor wrapper for Python, SQL Server, PySpark, Java.
 */
export default function CodeStudioEditor({
  language = 'python',
  value = '',
  onChange,
  height = '420px',
  readOnly = false,
}) {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-300 shadow-inner">
      <Editor
        height={height}
        theme="vs-dark"
        language={language}
        value={value}
        onChange={(v) => onChange?.(v ?? '')}
        options={{
          ...DEFAULT_OPTIONS,
          readOnly,
        }}
      />
    </div>
  );
}
