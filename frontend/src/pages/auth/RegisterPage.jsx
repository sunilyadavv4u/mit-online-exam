import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { AuthLayout } from './LoginPage';
import { useAuth } from '../../contexts/AuthContext';
import Spinner from '../../components/common/Spinner';

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    password: '',
    password_confirm: '',
    role: 'student',
  });
  const [loading, setLoading] = useState(false);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    if (form.password !== form.password_confirm) {
      return toast.error("Passwords don't match");
    }
    setLoading(true);
    try {
      await register(form);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      const detail =
        err.response?.data?.email?.[0] ||
        err.response?.data?.password?.[0] ||
        err.response?.data?.detail ||
        'Could not register, please try again.';
      toast.error(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout title="Create your account" subtitle="Join Mewati Institute of Technology - it's free.">
      <form onSubmit={onSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">First name</label>
            <input className="input" name="first_name" value={form.first_name} onChange={onChange} required />
          </div>
          <div>
            <label className="label">Last name</label>
            <input className="input" name="last_name" value={form.last_name} onChange={onChange} required />
          </div>
        </div>
        <div>
          <label className="label">Email</label>
          <input type="email" className="input" name="email" value={form.email} onChange={onChange} required />
        </div>
        <div>
          <label className="label">Phone (optional)</label>
          <input className="input" name="phone" value={form.phone} onChange={onChange} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Password</label>
            <input type="password" className="input" name="password" value={form.password} onChange={onChange} required minLength={8} />
          </div>
          <div>
            <label className="label">Confirm</label>
            <input type="password" className="input" name="password_confirm" value={form.password_confirm} onChange={onChange} required minLength={8} />
          </div>
        </div>
        <div>
          <label className="label">I am a</label>
          <div className="grid grid-cols-2 gap-3">
            {['student', 'teacher'].map((r) => (
              <label key={r} className={`cursor-pointer rounded-lg border px-4 py-3 text-center text-sm font-medium capitalize transition ${form.role === r ? 'border-primary-500 bg-primary-50 text-primary-700' : 'border-slate-300 text-slate-700 hover:bg-slate-50'}`}>
                <input type="radio" name="role" value={r} checked={form.role === r} onChange={onChange} className="sr-only" />
                {r}
              </label>
            ))}
          </div>
        </div>
        <button type="submit" className="btn-primary w-full" disabled={loading}>
          {loading && <Spinner size="sm" className="text-white" />} Create account
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-slate-600">
        Already have an account?{' '}
        <Link to="/login" className="font-semibold text-primary-600 hover:text-primary-700">Login</Link>
      </p>
    </AuthLayout>
  );
}
