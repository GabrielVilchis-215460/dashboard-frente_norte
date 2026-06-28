// -- Esqueleto principal de cada pestaña --

import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import styles from './AppLayout.module.css';

export function AppLayout() {
  return (
    <div className={styles.shell}>
      <Sidebar />
      <main className={styles.content}>
        <div className={styles.inner}>
          <Outlet />
        </div>
      </main>
    </div>
  );
}
