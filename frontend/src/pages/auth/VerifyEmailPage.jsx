import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { AuthLayout } from './LoginPage';
import { authApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';

export default function VerifyEmailPage() {
  const { token } = useParams();
  const [state, setState] = useState('verifying');

  useEffect(() => {
    authApi
      .verifyEmail(token)
      .then(() => setState('ok'))
      .catch(() => setState('error'));
  }, [token]);

  return (
    <AuthLayout title="Verify your email" subtitle="">
      <div className="card p-8 text-center">
        {state === 'verifying' && <Spinner size="lg" />}
        {state === 'ok' && (
          <>
            <p className="text-emerald-600 font-semibold">Email verified successfully.</p>
            <Link to="/login" className="btn-primary mt-4">Continue to login</Link>
          </>
        )}
        {state === 'error' && (
          <>
            <p className="text-red-600 font-semibold">This verification link is invalid or expired.</p>
            <Link to="/login" className="btn-secondary mt-4">Back to login</Link>
          </>
        )}
      </div>
    </AuthLayout>
  );
}
