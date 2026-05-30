import { useAuth } from '../contexts/AuthContext';
import StudentDashboard from './student/StudentDashboard';
import TeacherDashboard from './teacher/TeacherDashboard';
import AdminDashboard from './admin/AdminDashboard';

export default function DashboardRouter() {
  const { user } = useAuth();
  if (!user) return null;
  if (user.role === 'super_admin') return <AdminDashboard />;
  if (user.role === 'teacher') return <TeacherDashboard />;
  return <StudentDashboard />;
}
