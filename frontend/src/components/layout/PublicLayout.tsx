import { Link, Outlet } from 'react-router-dom';
import { ROUTES } from '../../constants/routes';
import styles from './PublicLayout.module.css';

export function PublicLayout() {
  return (
    <div className={styles.shell}>
      <header className={styles.nav}>
        <Link to={ROUTES.EVENTS} className={styles.navLink}>Explorar</Link>
        <Link to={`${ROUTES.EVENTS}?orden=populares`} className={styles.navLink}>Popular</Link>

        <Link to={ROUTES.HOME} className={styles.logo} aria-label="Frente Norte">
          <img src="/frente_norte_logo.png" alt="" className={styles.logoImg} />
        </Link>

        <a href={`${ROUTES.HOME}#mapa`} className={styles.navLink}>Mapa</a>
        <Link to={ROUTES.ABOUT} className={styles.navLink}>Acerca de</Link>
      </header>

      <main className={styles.main}>
        <Outlet />
      </main>

      <footer className={styles.footer}>
        <div className={styles.footerBrand}>
          <img src="/frente_norte_logo.png" alt="" className={styles.footerLogoImg} />
          <div>
            <div className={styles.footerTitle}>Frente Norte</div>
            <div className={styles.footerSubtitle}>Ecosistema STEM - Eventos</div>
          </div>
        </div>

        <nav className={styles.footerLinks}>
          <Link to={ROUTES.EVENTS}>Eventos</Link>
          <a href={`${ROUTES.HOME}#mapa`}>Mapa</a>
          <Link to={ROUTES.ABOUT}>Acerca de</Link>
          <Link to={ROUTES.OVERVIEW}>Dashboard STEM</Link>
        </nav>
      </footer>
    </div>
  );
}