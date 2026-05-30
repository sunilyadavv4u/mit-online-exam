import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import Spinner from './Spinner';

/**
 * Wraps a route or a tree of routes with auth + role gating.
 *
 * Usage 1 (single page):
 *   <ProtectedRoute roles={['teacher']}><MyPage /></ProtectedRoute>
 *
 * Usage 2 (route layout, nested routes provide the children):
 *   <Route element={<ProtectedRoute roles={['teacher']} />}>
 *     <Route path="/foo" element={<Foo />} />
 *   </Route>
 */
export default function ProtectedRoute({ children, roles }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;

  if (roles && roles.length > 0 && !roles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return children ?? <Outlet />;
}
