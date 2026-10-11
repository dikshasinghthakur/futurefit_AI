import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../lib/auth';

export default function ProtectedRoute({ children }) {
  const { user, booting } = useAuth();
  const location = useLocation();
  if (booting) return <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center' }}><div className="spinner dark" style={{ width: 28, height: 28 }} /></div>;
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return children;
}
