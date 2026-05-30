import { Route, Routes } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import ProtectedRoute from './components/common/ProtectedRoute';

import LandingPage from './pages/LandingPage';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import ResetPasswordPage from './pages/auth/ResetPasswordPage';
import VerifyEmailPage from './pages/auth/VerifyEmailPage';

import DashboardRouter from './pages/DashboardRouter';
import ExamsRouter from './pages/shared/ExamsRouter';
import ProfilePage from './pages/shared/ProfilePage';
import SettingsPage from './pages/shared/SettingsPage';
import NotificationsPage from './pages/shared/NotificationsPage';
import LeaderboardPage from './pages/shared/LeaderboardPage';
import AIAssistantPage from './pages/shared/AIAssistantPage';
import MITChatPage from './pages/shared/MITChatPage';
import CodeStudioPage from './pages/shared/CodeStudioPage';

import StudentExamAttemptPage from './pages/student/StudentExamAttemptPage';
import StudentResultsPage from './pages/student/StudentResultsPage';
import StudentResultDetailPage from './pages/student/StudentResultDetailPage';

import TeacherExamEditorPage from './pages/teacher/TeacherExamEditorPage';
import TeacherSubjectsPage from './pages/teacher/TeacherSubjectsPage';
import TeacherQuestionBankPage from './pages/teacher/TeacherQuestionBankPage';
import TeacherEvaluationsPage from './pages/teacher/TeacherEvaluationsPage';
import TeacherEvaluationDetailPage from './pages/teacher/TeacherEvaluationDetailPage';
import TeacherStudentsPage from './pages/teacher/TeacherStudentsPage';
import TeacherReportsPage from './pages/teacher/TeacherReportsPage';
import TeacherQuestionPaperPage from './pages/teacher/TeacherQuestionPaperPage';

import AdminUsersPage from './pages/admin/AdminUsersPage';
import AdminAuditLogsPage from './pages/admin/AdminAuditLogsPage';
import AdminSystemPage from './pages/admin/AdminSystemPage';

import NotFoundPage from './pages/NotFoundPage';

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route path="/verify-email/:token" element={<VerifyEmailPage />} />

      {/* Authenticated layout */}
      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardRouter />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/leaderboard" element={<LeaderboardPage />} />
        <Route path="/ai-assistant" element={<AIAssistantPage />} />
        <Route path="/mit-chat" element={<MITChatPage />} />
        <Route path="/code-studio" element={<CodeStudioPage />} />

        {/* Role-aware exams listing */}
        <Route path="/exams" element={<ExamsRouter />} />

        {/* Student-only routes */}
        <Route element={<ProtectedRoute roles={['student']} />}>
          <Route path="/exams/:slug/attempt" element={<StudentExamAttemptPage />} />
          <Route path="/results" element={<StudentResultsPage />} />
          <Route path="/results/:attemptId" element={<StudentResultDetailPage />} />
        </Route>

        {/* Teacher / super-admin routes */}
        <Route element={<ProtectedRoute roles={['teacher', 'super_admin']} />}>
          <Route path="/exams/new" element={<TeacherExamEditorPage />} />
          <Route path="/exams/:slug/edit" element={<TeacherExamEditorPage />} />
          {/* Backwards-compatible aliases */}
          <Route path="/exams/manage" element={<ExamsRouter />} />
          <Route path="/exams/manage/new" element={<TeacherExamEditorPage />} />
          <Route path="/exams/manage/:slug" element={<TeacherExamEditorPage />} />
          <Route path="/subjects" element={<TeacherSubjectsPage />} />
          <Route path="/question-bank" element={<TeacherQuestionBankPage />} />
          <Route path="/evaluations" element={<TeacherEvaluationsPage />} />
          <Route path="/evaluations/:id" element={<TeacherEvaluationDetailPage />} />
          <Route path="/students" element={<TeacherStudentsPage />} />
          <Route path="/reports" element={<TeacherReportsPage />} />
          <Route path="/ai-question-paper" element={<TeacherQuestionPaperPage />} />
        </Route>

        {/* Super admin only */}
        <Route element={<ProtectedRoute roles={['super_admin']} />}>
          <Route path="/users" element={<AdminUsersPage />} />
          <Route path="/audit-logs" element={<AdminAuditLogsPage />} />
          <Route path="/system" element={<AdminSystemPage />} />
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
