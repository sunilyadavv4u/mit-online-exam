import { Link } from 'react-router-dom';
import {
  Users,
  BookOpen,
  ClipboardList,
  GraduationCap,
  TrendingUp,
  BarChart3,
  ArrowRight,
} from 'lucide-react';
import { useFetch } from '../../hooks/useFetch';
import { analyticsApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';
import { formatDate } from '../../utils/helpers';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function TeacherDashboard() {
  const { data, loading } = useFetch(() => analyticsApi.teacherDashboard(), []);

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Teacher Overview</h1>
        <p className="text-slate-600">Manage exams, evaluations and student progress.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total Students"
          value={data?.total_students || 0}
          icon={Users}
          color="primary"
          to="/students"
        />
        <StatCard
          label="Total Exams"
          value={data?.total_exams || 0}
          icon={BookOpen}
          color="emerald"
          to="/exams"
        />
        <StatCard
          label="Active Exams"
          value={data?.active_exams || 0}
          icon={TrendingUp}
          color="amber"
          to="/exams?status=live"
        />
        <StatCard
          label="Pending Evaluations"
          value={data?.pending_evaluations || 0}
          icon={ClipboardList}
          color="rose"
          to="/evaluations"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="card p-6 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-900">Submissions in last 7 days</h2>
            <BarChart3 className="h-5 w-5 text-slate-400" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.attempts_by_day || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="day" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-900">Performance</h2>
            <Link
              to="/leaderboard"
              className="text-sm font-medium text-primary-600 hover:text-primary-700"
            >
              Leaderboard →
            </Link>
          </div>
          <div className="space-y-4">
            <Metric label="Pass percentage" value={`${(data?.pass_percentage || 0).toFixed(1)}%`} />
            <Metric label="Average score" value={(data?.average_score || 0).toFixed(2)} />
            <Metric label="Recent attempts" value={data?.recent_attempts || 0} />
          </div>
        </div>
      </div>

      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-slate-900">Upcoming exams</h2>
          <Link
            to="/exams"
            className="text-sm font-medium text-primary-600 hover:text-primary-700"
          >
            Manage all →
          </Link>
        </div>
        {(!data?.upcoming_exams || data.upcoming_exams.length === 0) ? (
          <p className="text-slate-500">No upcoming exams scheduled.</p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {data.upcoming_exams.map((e) => (
              <li key={e.id}>
                <Link
                  to={e.slug ? `/exams/${e.slug}/edit` : '/exams'}
                  className="flex items-center justify-between py-3 -mx-2 px-2 rounded-lg hover:bg-slate-50 transition"
                >
                  <div>
                    <p className="font-medium text-slate-900">{e.title}</p>
                    <p className="text-xs text-slate-500">
                      {e.subject__name} • Starts {formatDate(e.start_time)}
                    </p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-slate-400" />
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, icon: Icon, color, to }) {
  const colorMap = {
    primary: 'bg-primary-50 text-primary-600',
    emerald: 'bg-emerald-50 text-emerald-600',
    amber: 'bg-amber-50 text-amber-600',
    rose: 'bg-rose-50 text-rose-600',
  };
  const inner = (
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-slate-500">{label}</p>
        <p className="mt-2 text-2xl font-bold text-slate-900">{value}</p>
      </div>
      <div className={`h-12 w-12 rounded-xl flex items-center justify-center ${colorMap[color]}`}>
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

function Metric({ label, value }) {
  return (
    <div className="flex items-center justify-between">
      <p className="text-sm text-slate-600">{label}</p>
      <p className="font-bold text-slate-900">{value}</p>
    </div>
  );
}
