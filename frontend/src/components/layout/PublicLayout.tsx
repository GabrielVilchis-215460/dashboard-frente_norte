import { useState } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { IconMenu2, IconX } from '@tabler/icons-react';
import { ROUTES } from '../../constants/routes';
import styles from './PublicLayout.module.css';

const pageVariants = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.28, ease: [0.22, 1, 0.36, 1] } },
  exit:    { opacity: 0,        transition: { duration: 0.15, ease: 'easeIn' } },
};

export function PublicLayout() {
  const [menuAbierto, setMenuAbierto] = useState(false);
  const location = useLocation();

  const links = (
    <>
      <Link to={ROUTES.EVENTS} className={styles.navLink} onClick={() => setMenuAbierto(false)}>
        Explorar
      </Link>
      <Link
        to={`${ROUTES.EVENTS}?orden=populares`}
        className={styles.navLink}
        onClick={() => setMenuAbierto(false)}
      >
        Popular
      </Link>
    </>
  );

  const linksDerecha = (
    <>
      <a href={`${ROUTES.HOME}#mapa`} className={styles.navLink} onClick={() => setMenuAbierto(false)}>
        Mapa
      </a>
      <Link to={ROUTES.ABOUT} className={styles.navLink} onClick={() => setMenuAbierto(false)}>
        Acerca de
      </Link>
    </>
  );

  return (
    <div className={`${styles.shell} theme-public`}>
      <div className={styles.aurora} aria-hidden="true">
        <div className={styles.auroraBand1} />
        <div className={styles.auroraBand2} />
        <div className={styles.auroraBand3} />
      </div>

      <header className={styles.nav}>
        <div className={styles.navSideDesktop}>{links}</div>

        <Link to={ROUTES.HOME} className={styles.logo} aria-label="Frente Norte">
          <img src="/frente_norte_logo.png" alt="" className={styles.logoImg} />
        </Link>

        <div className={styles.navSideDesktop}>{linksDerecha}</div>

        <button
          type="button"
          className={styles.menuBtn}
          aria-label={menuAbierto ? 'Cerrar menú' : 'Abrir menú'}
          onClick={() => setMenuAbierto((v) => !v)}
        >
          {menuAbierto ? <IconX size={22} stroke={1.8} /> : <IconMenu2 size={22} stroke={1.8} />}
        </button>
      </header>

      {menuAbierto && (
        <div className={styles.mobileDrawer}>
          {links}
          {linksDerecha}
        </div>
      )}

      <main className={styles.main}>
        <AnimatePresence mode="wait" initial={false}>
          <motion.div key={location.pathname} variants={pageVariants} initial="initial" animate="animate" exit="exit">
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>

      <footer className={styles.footer}>
        <div className={styles.footerInner}>
          <div className={styles.footerBrand}>
            <img src="/frente_norte_logo.png" alt="" className={styles.footerLogoImg} />
            <div>
              <div className={styles.footerTitle}>Frente Norte</div>
              <div className={styles.footerSubtitle}>Ecosistema STEM &ndash; Eventos</div>
            </div>
          </div>

          <nav className={styles.footerLinks}>
            <Link to={ROUTES.EVENTS}>Eventos</Link>
            <a href={`${ROUTES.HOME}#mapa`}>Mapa</a>
            <Link to={ROUTES.ABOUT}>Acerca de</Link>
            <Link to={ROUTES.OVERVIEW}>Dashboard STEM</Link>
          </nav>
        </div>
      </footer>
    </div>
  );
}