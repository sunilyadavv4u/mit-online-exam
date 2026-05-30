import { Link } from 'react-router-dom';
import { BookOpen, GraduationCap, Trophy, Clock, ArrowRight, CheckCircle2 } from 'lucide-react';
import { useFetch } from '../../hooks/useFetch';
import { analyticsApi, examsApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';
import EmptyState from '../../components/common/EmptyState';
import { formatDate } from '../../utils/helpers';
import { useAuth } from '../../contexts/AuthContext';

export default function StudentDashboard() {
  const { user } = useAuth();
  const { data: dash, loading } = useFetch(() => analyticsApi.studentDashboard(), []);
  const { data: upcomingResp } = useFetch(() => examsApi.myUpcoming(), []);
  const upcoming = Array.isArray(upcomingResp) ? upcomingResp : [];

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Welcome, {user?.first_name || 'student'}!
        </h1>
        <p className="text-slate-600">Here's what's happening with your exams today.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Upcoming Exams"
          value={dash?.upcoming_exams?.length || 0}
          icon={Clock}
          color="primary"
          to="/exams"
        />
        <StatCard
          label="Completed"
          value={dash?.completed_exams || 0}
          icon={CheckCircle2}
          color="emerald"
          to="/results"
        />
        <StatCard
          label="Passed"
          value={dash?.passed_exams || 0}
          icon={Trophy}
          color="amber"
          to="/results"
        />
        <StatCard
          label="Average Score"
          value={(dash?.average_score || 0).toFixed(1)}
          icon={GraduationCap}
          color="indigo"
          to="/leaderboard"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="card p-6 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-900">Upcoming exams</h2>
            <Link to="/exams" className="text-sm font-medium text-primary-600 hover:text-primary-700">View all</Link>
          </div>
          {(!upcoming || upcoming.length === 0) ? (
            <EmptyState icon={BookOpen} title="No exams scheduled" description="Your teacher hasn't scheduled any exams yet." />
          ) : (
            <ul className="divide-y divide-slate-100">
              {upcoming.slice(0, 5).map((exam) => (
                <li key={exam.id}>
                  <Link
                    to="/exams"
                    className="flex items-center justify-between py-3 -mx-2 px-2 rounded-lg hover:bg-slate-50 transition"
                  >
                    <div>
                      <p className="font-medium text-slate-900">{exam.title}</p>
                      <p className="text-xs text-slate-500">
                        {exam.subject_name} • {exam.duration_minutes} min • Starts {formatDate(exam.start_time)}
                      </p>
                    </div>
                    <span className="btn-primary py-1.5 px-3 pointer-events-none">
                      Open <ArrowRight className="h-4 w-4" />
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-900">Recent results</h2>
            <Link to="/results" className="text-sm font-medium text-primary-600 hover:text-primary-700">
              View all →
            </Link>
          </div>
          {(!dash?.recent_results || dash.recent_results.length === 0) ? (
            <EmptyState icon={Trophy} title="No results yet" description="Your results will appear once your teacher publishes them." />
          ) : (
            <ul className="space-y-3">
              {dash.recent_results.map((r) => (
                <li key={r.id}>
                  <Link
                    to={`/results/${r.id}`}
                    className="block rounded-lg border border-slate-200 p-3 hover:border-primary-300 hover:shadow-sm transition"
                  >
                    <p className="font-medium text-slate-900">{r.exam__title}</p>
                    <p className="text-xs text-slate-500">{r.exam__subject__name}</p>
                    <div className="mt-2 flex items-center justify-between">
                      <span className={`badge ${r.is_passed ? 'badge-success' : 'badge-warning'}`}>
                        {r.is_passed ? 'Passed' : 'Not Passed'}
                      </span>
                      <span className="font-semibold text-slate-900">{Number(r.total_score).toFixed(1)}</span>
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon: Icon, color, to }) {
  const colorMap = {
    primary: 'from-primary-500 to-primary-700',
    emerald: 'from-emerald-500 to-emerald-700',
    amber: 'from-amber-500 to-amber-700',
    indigo: 'from-indigo-500 to-indigo-700',
  };
  const inner = (
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-slate-500">{label}</p>
        <p className="mt-2 text-2xl font-bold text-slate-900">{value}</p>
      </div>
      <div className={`h-12 w-12 rounded-xl bg-gradient-to-br ${colorMap[color]} flex items-center justify-center text-white`}>
        <Icon className="h-6 w-6" />
      </div>
    </div>
  );
  if (!to) return <div className="card p-5">{inner}</div>;
  return (
    <Link
      to={to}
      className="card p-5 block transition hover:-translate-y-0.5 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
      aria-label={`${label}: ${value}`}
    >
      {inner}
    </Link>
  );
}
