import { useState } from 'react';
import { useFetch } from '../../hooks/useFetch';
import { questionsApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';
import { Search } from 'lucide-react';

export default function TeacherQuestionBankPage() {
  const [q, setQ] = useState('');
  const [type, setType] = useState('');
  const params = { is_in_bank: true, search: q || undefined, question_type: type || undefined, page_size: 50 };
  const { data, loading } = useFetch(() => questionsApi.list(params), [q, type]);
  const list = data?.results || data || [];

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Question Bank</h1>
        <p className="text-slate-600">Browse and reuse existing questions.</p>
      </div>

      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input placeholder="Search questions..." value={q} onChange={(e) => setQ(e.target.value)} className="input pl-9" />
        </div>
        <select value={type} onChange={(e) => setType(e.target.value)} className="input max-w-[200px]">
          <option value="">All types</option>
          <option value="single_choice">Single Choice</option>
          <option value="multiple_choice">Multiple Choice</option>
          <option value="true_false">True/False</option>
          <option value="fill_blank">Fill Blank</option>
          <option value="descriptive">Descriptive</option>
          <option value="coding">Coding</option>
        </select>
      </div>

      {loading ? <Spinner /> : (
        <ul className="space-y-3">
          {list.map((q, i) => (
            <li key={q.id} className="card p-4">
              <p className="text-xs uppercase tracking-wide text-slate-500 font-semibold">
                {q.question_type.replace('_', ' ')} • {q.difficulty} • {q.marks} marks
              </p>
              <p className="mt-1 font-medium text-slate-900">{q.text}</p>
            </li>
          ))}
          {list.length === 0 && <p className="text-slate-500">No questions found.</p>}
        </ul>
      )}
    </div>
  );
}
