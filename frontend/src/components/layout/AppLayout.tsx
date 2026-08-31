// -- Esqueleto principal de cada pestaña --

import { useState, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { Sidebar } from './Sidebar';
import { ROUTES } from '../../constants/routes';
import styles from './AppLayout.module.css';

const pageVariants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.3, ease: [0.22, 1, 0.36, 1] } },
  exit:    { opacity: 0,       transition: { duration: 0.15, ease: 'easeIn' } },
};

const ROUTE_THEME: Record<string, string> = {
  [ROUTES.OVERVIEW]:      'theme-navy',
  [ROUTES.STEM_OFFER]:    'theme-navy',
  [ROUTES.HEALTH]:          'theme-navy',
  [ROUTES.BENEFICIARIES]: 'theme-teal',
  [ROUTES.MATURITY]:      'theme-teal',
  [ROUTES.EVENTS_TAB]:  'theme-teal',
  [ROUTES.INCLUSION]:     'theme-cyan',
  [ROUTES.MAP]:           'theme-cyan',
  [ROUTES.ADMIN]:         'theme-cyan',
};

function getTheme(pathname: string): string {
  return ROUTE_THEME[pathname] ?? 'theme-navy';
}

function HamburgerIcon({ open }: { open: boolean }) {
  return (
    <div className={`${styles.hamburgerIcon} ${open ? styles.hamburgerOpen : ''}`}>
      <span /><span /><span />
    </div>
  );
}

export function AppLayout() {
  const location = useLocation();
  const theme = getTheme(location.pathname);
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Cierra el drawer al navegar
  useEffect(() => { setDrawerOpen(false); }, [location.pathname]);

  return (
    <div className={`${styles.shell} ${theme}`}>
      {/* Sidebar desktop — tarjeta glass (oculto en móvil vía CSS) */}
      <aside className={styles.sidebarWrapper}>
        <Sidebar />
      </aside>

      {/* Botón hamburguesa — solo móvil */}
      <button
        className={styles.hamburgerBtn}
        onClick={() => setDrawerOpen((o) => !o)}
        aria-label="Abrir menú"
      >
        <HamburgerIcon open={drawerOpen} />
      </button>

      {/* Overlay oscuro */}
      {drawerOpen && (
        <div className={styles.drawerOverlay} onClick={() => setDrawerOpen(false)} />
      )}

      {/* Drawer deslizable desde la izquierda */}
      <div className={`${styles.drawer} ${drawerOpen ? styles.drawerOpen : ''}`}>
        <Sidebar />
      </div>

      {/* Contenido principal como tarjeta glass */}
      <main className={styles.contentGlass}>
        <div className={styles.inner}>
          <AnimatePresence mode="wait" initial={false}>
            <motion.div key={location.pathname} variants={pageVariants} initial="initial" animate="animate" exit="exit">
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}