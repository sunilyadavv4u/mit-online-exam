import { useState } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { AuthLayout } from './LoginPage';
import { authApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await authApi.forgotPassword(email);
      setDone(true);
      toast.success('Check your email for the reset link');
    } catch {
      toast.error('Could not send reset email');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout title="Forgot password?" subtitle="Enter your email - we'll send you a reset link.">
      {done ? (
        <div className="card p-6 text-center">
          <p className="text-slate-700">If an account exists for <strong>{email}</strong>, a reset link has been sent.</p>
          <Link to="/login" className="btn-secondary mt-4">Back to login</Link>
        </div>
      ) : (
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="label">Email</label>
            <input
              type="email"
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <button className="btn-primary w-full" disabled={loading}>
            {loading && <Spinner size="sm" className="text-white" />} Send reset link
          </button>
          <p className="text-center text-sm text-slate-600">
            <Link to="/login" className="font-semibold text-primary-600">Back to login</Link>
          </p>
        </form>
      )}
    </AuthLayout>
  );
}
