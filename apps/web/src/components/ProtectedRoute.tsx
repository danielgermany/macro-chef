import type { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { token, isReady } = useAuth();

  if (!isReady) {
    return (
      <div style={{ padding: '2rem', fontFamily: 'system-ui' }}>
        <p>Loading session…</p>
      </div>
    );
  }

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
