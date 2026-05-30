import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { AuthLayout } from './LoginPage';
import { authApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';

export default function ResetPasswordPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const [token, setToken] = useState(params.get('token') || '');
  const [pwd, setPwd] = useState('');
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await authApi.resetPassword(token, pwd);
      toast.success('Password reset. Please log in.');
      navigate('/login');
    } catch {
      toast.error('Token may be invalid or expired');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout title="Reset password" subtitle="Set a new password to access your account.">
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="label">Token</label>
          <input className="input" value={token} onChange={(e) => setToken(e.target.value)} required />
        </div>
        <div>
          <label className="label">New password</label>
          <input type="password" className="input" value={pwd} onChange={(e) => setPwd(e.target.value)} required minLength={8} />
        </div>
        <button className="btn-primary w-full" disabled={loading}>
          {loading && <Spinner size="sm" className="text-white" />} Reset password
        </button>
        <p className="text-center text-sm text-slate-600">
          <Link to="/login" className="font-semibold text-primary-600">Back to login</Link>
        </p>
      </form>
    </AuthLayout>
  );
}
