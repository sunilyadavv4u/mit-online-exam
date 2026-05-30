import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import InstituteBrand from '../../components/layout/InstituteBrand';
import toast from 'react-hot-toast';
import { useAuth } from '../../contexts/AuthContext';
import Spinner from '../../components/common/Spinner';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const user = await login(email, password);
      const dest = location.state?.from || '/dashboard';
      navigate(dest, { replace: true });
    } catch (err) {
      const detail = err.response?.data?.detail || 'Invalid credentials';
      toast.error(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout title="Welcome back" subtitle="Login to continue your exam journey.">
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="label">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input"
            placeholder="you@example.com"
            required
            autoComplete="email"
          />
        </div>
        <div>
          <div className="flex items-center justify-between">
            <label htmlFor="password" className="label mb-0">Password</label>
            <Link to="/forgot-password" className="text-xs font-medium text-primary-600 hover:text-primary-700">
              Forgot password?
            </Link>
          </div>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input"
            placeholder="••••••••"
            required
            autoComplete="current-password"
          />
        </div>
        <button type="submit" className="btn-primary w-full" disabled={loading}>
          {loading && <Spinner size="sm" className="text-white" />} Login
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-600">
        Don't have an account?{' '}
        <Link to="/register" className="font-semibold text-primary-600 hover:text-primary-700">
          Sign up
        </Link>
      </p>
    </AuthLayout>
  );
}

export function AuthLayout({ title, subtitle, children }) {
  return (
    <div className="min-h-screen flex">
      <div className="hidden lg:flex flex-1 bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 text-white p-12 flex-col justify-between">
        <InstituteBrand variant="onDark" />
        <div>
          <h1 className="text-4xl font-extrabold leading-tight">
            Examinations made <br /> fair, fast & free.
          </h1>
          <p className="mt-4 text-primary-100 max-w-md leading-relaxed">
            Auto-graded MCQs, secure proctoring, AI-powered code conversion - all included.
          </p>
        </div>
        <p className="text-xs text-primary-200">
          © {new Date().getFullYear()} Mewati Institute of Technology
        </p>
      </div>
      <div className="flex flex-1 items-center justify-center p-6">
        <div className="w-full max-w-md">
          <div className="lg:hidden mb-6">
            <InstituteBrand />
          </div>
          <h2 className="text-3xl font-bold text-slate-900">{title}</h2>
          {subtitle && <p className="mt-2 text-slate-600">{subtitle}</p>}
          <div className="mt-8">{children}</div>
        </div>
      </div>
    </div>
  );
}
