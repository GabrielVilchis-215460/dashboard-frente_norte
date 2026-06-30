import { Navigate } from 'react-router-dom';
import { authStorage } from '../../services/adminApi';

export function RequireAuth({ children }: { children: React.ReactNode }) {
  return authStorage.getToken() ? <>{children}</> : <Navigate to="/admin/login" replace />;
}
