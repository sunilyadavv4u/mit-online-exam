import { Link } from 'react-router-dom';
import { useFetch } from '../../hooks/useFetch';
import { analyticsApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';
import { Users, BookOpen, Activity, Clock } from 'lucide-react';
import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts';

const COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function AdminDashboard() {
  const { data, loading } = useFetch(() => analyticsApi.superAdminDashboard(), []);

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">System Overview</h1>
        <p className="text-slate-600">High level system metrics for super admins.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Stat label="Total users" value={data?.total_users || 0} icon={Users} to="/users" />
        <Stat label="Active users" value={data?.active_users || 0} icon={Users} to="/users?is_active=true" />
        <Stat label="Total attempts" value={data?.total_attempts || 0} icon={Activity} to="/audit-logs" />
        <Stat label="Live exams" value={data?.live_exams || 0} icon={BookOpen} to="/exams?status=live" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card p-6">
          <h2 className="font-semibold text-slate-900 mb-4">Users by role</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={data?.users_by_role || []} dataKey="count" nameKey="role" outerRadius={90} label>
                  {(data?.users_by_role || []).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card p-6 space-y-4">
          <h2 className="font-semibold text-slate-900">Recent activity</h2>
          <Metric icon={Clock} label="Registrations (last 30 days)" value={data?.registrations_last_30_days || 0} />
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value, icon: Icon, to }) {
  const inner = (
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-slate-500">{label}</p>
        <p className="mt-2 text-2xl font-bold text-slate-900">{value}</p>
      </div>
      <div className="h-12 w-12 rounded-xl bg-primary-50 text-primary-600 flex items-center justify-center">
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

function Metric({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <Icon className="h-5 w-5 text-slate-400" />
        <p className="text-sm text-slate-700">{label}</p>
      </div>
      <p className="font-bold text-slate-900">{value}</p>
    </div>
  );
}
