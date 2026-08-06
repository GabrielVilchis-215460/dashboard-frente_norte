// -- Sidebar (Navegacion) --

import { NavLink, Link } from 'react-router-dom';
import {
  IconChartBar,
  IconUsers,
  IconVenus,
  IconFlask,
  IconTrendingUp,
  IconMap,
  IconActivity,
  IconSettings,
  IconCalendarEvent,
  IconArrowLeft,
} from '@tabler/icons-react';
import { NAV_ITEMS } from '../../constants/navigation';
import { ROUTES } from '../../constants/routes';
import { useDashboardStore } from '../../store/dashboardStore';
import { authStorage } from '../../services/adminApi';
import { LogoutButton } from '../common/LogoutButton';
import styles from './Sidebar.module.css';

// Map de iconos — extensible sin tocar el componente
const ICON_MAP: Record<string, React.ComponentType<any>> = {
  IconChartBar,
  IconUsers,
  IconVenus,
  IconFlask,
  IconTrendingUp,
  IconMap,
  IconActivity,
  IconSettings,
  IconCalendarEvent,
};

function NavIcon({ name, size = 18 }: { name: string; size?: number }) {
  const Icon = ICON_MAP[name];
  return Icon ? <Icon size={size} stroke={1.5} /> : null;
}

export function Sidebar() {
  const lastUpdated = useDashboardStore((s) => s.lastUpdated);
  const esAdmin = authStorage.getRol() === 'admin';

  return (
    <aside className={styles.sidebar}>
      {/* Logo / Brand */}
      <div className={styles.brand}>
        <img
          src="/frente_norte_logo.png"
          alt="Frente Norte"
          className={styles.logoIcon}
        />
        <span className={styles.brandName}>Frente Norte</span>
      </div>

      {/* Nav items */}
      <nav className={styles.nav}>
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.key}
            to={item.path}
            end={item.path === ROUTES.OVERVIEW}
            className={({ isActive }) =>
              `${styles.navItem} ${isActive ? styles.navItemActive : ''}`
            }
          >
            <span className={styles.navIcon}>
              <NavIcon name={item.icon} />
            </span>
            <span className={styles.navLabel}>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className={styles.footer}>
        {lastUpdated && (
          <span className={styles.lastUpdated}>
            Última actualización: {lastUpdated}
          </span>
        )}

        <div className={styles.footerRow}>
          <div className={styles.footerLeft}>
            <Link to={ROUTES.HOME} className={styles.iconBtn} aria-label="Volver al sitio">
              <IconArrowLeft size={16} stroke={1.5} />
              <span>Volver</span>
            </Link>

            {esAdmin && (
              <NavLink
                to={ROUTES.ADMIN}
                className={({ isActive }) =>
                  `${styles.iconBtn} ${styles.iconBtnSquare} ${isActive ? styles.iconBtnActive : ''}`
                }
                aria-label="Panel de administración"
              >
                <IconSettings size={16} stroke={1.5} />
              </NavLink>
            )}
          </div>

          <LogoutButton className={styles.iconBtnSquare} />
        </div>
      </div>
    </aside>
  );
}
