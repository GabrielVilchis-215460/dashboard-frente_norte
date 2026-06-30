// -- Esqueleto principal de cada pestaña --

import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { ROUTES } from '../../constants/routes';
import styles from './AppLayout.module.css';

const ROUTE_THEME: Record<string, string> = {
  [ROUTES.OVERVIEW]:      'theme-navy',
  [ROUTES.STEM_OFFER]:    'theme-navy',
  [ROUTES.HEALTH]:          'theme-navy',
  [ROUTES.BENEFICIARIES]: 'theme-teal',
  [ROUTES.MATURITY]:      'theme-teal',
  [ROUTES.INCLUSION]:     'theme-cyan',
  [ROUTES.MAP]:           'theme-cyan',
  [ROUTES.ADMIN]:         'theme-cyan',
};

function getTheme(pathname: string): string {
  return ROUTE_THEME[pathname] ?? 'theme-navy';
}

export function AppLayout() {
  const location = useLocation();
  const theme = getTheme(location.pathname);

  return (
    <div className={`${styles.shell} ${theme}`}>
      {/* Sidebar como tarjeta glass */}
      <aside className={styles.sidebarWrapper}>
        <Sidebar />
      </aside>

      {/* Contenido principal como tarjeta glass */}
      <main className={styles.contentGlass}>
        <div className={styles.inner}>
          <Outlet />
        </div>
      </main>
    </div>
  );
}