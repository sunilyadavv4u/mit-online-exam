import { useState } from 'react';
import { Download, FileSpreadsheet, FileText } from 'lucide-react';
import toast from 'react-hot-toast';
import { useFetch } from '../../hooks/useFetch';
import { analyticsApi, examsApi } from '../../api/endpoints';
import { downloadBlob } from '../../utils/helpers';
import Spinner from '../../components/common/Spinner';

export default function TeacherReportsPage() {
  const { data: exams } = useFetch(() => examsApi.list({ page_size: 100 }), []);
  const list = exams?.results || [];
  const [examId, setExamId] = useState('');
  const [busy, setBusy] = useState(null);

  const dl = async (kind) => {
    setBusy(kind);
    try {
      const params = examId ? { exam_id: examId } : {};
      const fn = kind === 'csv' ? analyticsApi.attemptsCsv : analyticsApi.attemptsXlsx;
      const r = await fn(params);
      downloadBlob(r.data, kind === 'csv' ? 'attempts.csv' : 'attempts.xlsx');
      toast.success('Downloaded');
    } catch {
      toast.error('Download failed');
    } finally {
      setBusy(null);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Reports</h1>
        <p className="text-slate-600">Export attempts and results in CSV / Excel for offline analysis.</p>
      </div>

      <div className="card p-6 space-y-4">
        <div>
          <label className="label">Filter by exam (optional)</label>
          <select className="input max-w-md" value={examId} onChange={(e) => setExamId(e.target.value)}>
            <option value="">All exams</option>
            {list.map((e) => <option key={e.id} value={e.id}>{e.title}</option>)}
          </select>
        </div>
        <div className="flex gap-3">
          <button className="btn-primary" onClick={() => dl('csv')} disabled={busy === 'csv'}>
            <FileText className="h-4 w-4" /> {busy === 'csv' ? 'Preparing...' : 'Export CSV'}
          </button>
          <button className="btn-primary" onClick={() => dl('xlsx')} disabled={busy === 'xlsx'}>
            <FileSpreadsheet className="h-4 w-4" /> {busy === 'xlsx' ? 'Preparing...' : 'Export Excel'}
          </button>
        </div>
      </div>
    </div>
  );
}
