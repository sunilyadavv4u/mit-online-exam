import { useState } from 'react';
import { useFetch } from '../../hooks/useFetch';
import { analyticsApi, examsApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';
import { Trophy, Medal } from 'lucide-react';

export default function LeaderboardPage() {
  const [examId, setExamId] = useState('');
  const { data: exams } = useFetch(() => examsApi.list({ page_size: 100 }), []);
  const { data: lb, loading } = useFetch(() => analyticsApi.leaderboard(examId ? { exam_id: examId } : {}), [examId]);

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Leaderboard</h1>
        <p className="text-slate-600">Top performers across exams.</p>
      </div>

      <div>
        <label className="label">Filter by exam</label>
        <select className="input max-w-md" value={examId} onChange={(e) => setExamId(e.target.value)}>
          <option value="">All exams</option>
          {(exams?.results || []).map((e) => <option key={e.id} value={e.id}>{e.title}</option>)}
        </select>
      </div>

      {loading ? <Spinner /> : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Rank</th>
                <th className="px-4 py-3">Student</th>
                <th className="px-4 py-3">Avg Score</th>
                <th className="px-4 py-3">Attempts</th>
                <th className="px-4 py-3">Passed</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(lb || []).map((row, i) => (
                <tr key={row.student__id} className="hover:bg-slate-50">
                  <td className="px-4 py-3">
                    {i === 0 ? <Trophy className="h-5 w-5 text-amber-500" /> :
                     i === 1 ? <Medal className="h-5 w-5 text-slate-400" /> :
                     i === 2 ? <Medal className="h-5 w-5 text-amber-700" /> :
                     <span className="text-slate-500">#{i + 1}</span>}
                  </td>
                  <td className="px-4 py-3 font-medium text-slate-900">
                    {row.student__first_name} {row.student__last_name}
                    <p className="text-xs text-slate-500">{row.student__email}</p>
                  </td>
                  <td className="px-4 py-3 font-semibold">{Number(row.score || 0).toFixed(2)}</td>
                  <td className="px-4 py-3">{row.attempts}</td>
                  <td className="px-4 py-3">{row.passed}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
