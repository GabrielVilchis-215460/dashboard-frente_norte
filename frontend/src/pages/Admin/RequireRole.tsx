import { Navigate } from 'react-router-dom';
import { authStorage } from '../../services/adminApi';
import { ROUTES } from '../../constants/routes';

interface Props {
  roles: Array<'admin' | 'viewer'>;
  children: React.ReactNode;
}

/*
 * Protege una ruta exigiendo sesión iniciada y opcionalmente un rol específico.
 * Si no hay token -> redirige a login.
 * Si hay token con acceso limitado (viewer) -> redirige al overview del dashboard.
 *
 * Uso:
 *   <RequireRole roles={['viewer', 'admin']}> ... </RequireRole>   // cualquier sesión
 *   <RequireRole roles={['admin']}> ... </RequireRole>             // solo admin (CRUD)
 */
export function RequireRole({ roles, children }: Props) {
  const token = authStorage.getToken();
  if (!token) {
    return <Navigate to={ROUTES.LOGIN} replace />;
  }

  const rol = authStorage.getRol();
  if (!rol || !roles.includes(rol)) {
    return <Navigate to={ROUTES.OVERVIEW} replace />;
  }

  return <>{children}</>;
}