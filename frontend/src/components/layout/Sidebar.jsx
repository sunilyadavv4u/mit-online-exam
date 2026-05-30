import { NavLink } from 'react-router-dom';
import clsx from 'clsx';
import InstituteBrand from './InstituteBrand';
import {
  Home,
  LayoutDashboard,
  BookOpen,
  ClipboardList,
  GraduationCap,
  Bell,
  BarChart3,
  Users,
  Cpu,
  ShieldAlert,
  Sparkles,
  FileSpreadsheet,
  FileQuestion,
  MessageCircle,
  Code2,
} from 'lucide-react';

const MIT_CHAT_LINK = { to: '/mit-chat', label: 'MIT AI Chat', icon: MessageCircle };
const CODE_STUDIO_LINK = { to: '/code-studio', label: 'Code Studio', icon: Code2 };
import { useAuth } from '../../contexts/AuthContext';

const STUDENT_LINKS = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/exams', label: 'My Exams', icon: BookOpen },
  { to: '/results', label: 'My Results', icon: GraduationCap },
  { to: '/leaderboard', label: 'Leaderboard', icon: BarChart3 },
  { to: '/ai-assistant', label: 'AI Assistant', icon: Sparkles },
  MIT_CHAT_LINK,
  CODE_STUDIO_LINK,
  { to: '/notifications', label: 'Notifications', icon: Bell },
];

const TEACHER_LINKS = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/exams', label: 'Exams', icon: BookOpen },
  { to: '/subjects', label: 'Subjects', icon: ClipboardList },
  { to: '/question-bank', label: 'Question Bank', icon: ClipboardList },
  { to: '/evaluations', label: 'Evaluations', icon: GraduationCap },
  { to: '/students', label: 'Students', icon: Users },
  { to: '/reports', label: 'Reports', icon: FileSpreadsheet },
  { to: '/ai-question-paper', label: 'AI Question Paper', icon: FileQuestion },
  { to: '/ai-assistant', label: 'AI Assistant', icon: Sparkles },
  MIT_CHAT_LINK,
  CODE_STUDIO_LINK,
  { to: '/notifications', label: 'Notifications', icon: Bell },
];

const ADMIN_LINKS = [
  MIT_CHAT_LINK,
  CODE_STUDIO_LINK,
  { to: '/dashboard', label: 'Overview', icon: LayoutDashboard },
  { to: '/users', label: 'Users', icon: Users },
  { to: '/audit-logs', label: 'Audit Logs', icon: ShieldAlert },
  { to: '/system', label: 'System', icon: Cpu },
];

const linkSets = {
  student: STUDENT_LINKS,
  teacher: TEACHER_LINKS,
  super_admin: [...TEACHER_LINKS, ...ADMIN_LINKS.filter((l) => l.to !== '/dashboard')],
};

export default function Sidebar({ collapsed, onClose }) {
  const { user } = useAuth();
  const links = linkSets[user?.role] || STUDENT_LINKS;

  return (
    <aside
      className={clsx(
        'flex h-full flex-col bg-white border-r border-slate-200 transition-all duration-200',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      <div className="flex h-16 items-center border-b border-slate-200 px-4">
        <InstituteBrand collapsed={collapsed} />
      </div>

      <nav className="flex-1 overflow-y-auto p-3 space-y-1">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === '/' || link.to === '/dashboard'}
            onClick={onClose}
            className={({ isActive }) =>
              clsx('nav-link', isActive && 'nav-link-active', collapsed && 'justify-center')
            }
          >
            <link.icon className="h-5 w-5 shrink-0" />
            {!collapsed && <span>{link.label}</span>}
          </NavLink>
        ))}
      </nav>

      {!collapsed && (
        <div className="border-t border-slate-200 p-4 text-xs text-slate-500">
          <p className="font-semibold text-slate-700">{user?.full_name}</p>
          <p>{user?.email}</p>
          <p className="mt-1 capitalize">
            <span className="badge-primary">{user?.role?.replace('_', ' ')}</span>
          </p>
        </div>
      )}
    </aside>
  );
}
