import { useAuth } from '../../contexts/AuthContext';
import StudentExamsPage from '../student/StudentExamsPage';
import TeacherExamsPage from '../teacher/TeacherExamsPage';

/**
 * /exams → role-aware page: students see their enrolled exams,
 * teachers / admins see the management list with a "+ New exam" button.
 */
export default function ExamsRouter() {
  const { user } = useAuth();
  if (!user) return null;
  if (user.role === 'student') return <StudentExamsPage />;
  return <TeacherExamsPage />;
}
