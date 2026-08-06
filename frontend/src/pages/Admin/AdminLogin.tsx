import { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { IconArrowLeft } from '@tabler/icons-react';
import { adminApi, authStorage } from '../../services/adminApi';
import { ROUTES } from '../../constants/routes';
import styles from './AdminLogin.module.css';

export function AdminLogin() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const { access_token, rol } = await adminApi.login({ username, password });
      authStorage.setToken(access_token);
      authStorage.setRol(rol);
      navigate(ROUTES.OVERVIEW, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Credenciales incorrectas');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={`${styles.wrapper} theme-cyan`}>
      <div className={styles.card}>
        <Link to={ROUTES.HOME} className={styles.backLink} aria-label="Volver al sitio">
          <IconArrowLeft size={16} stroke={1.8} />
        </Link>

        <div className={styles.logo}>
          <img src="/frente_norte_logo.png" alt="Frente Norte" className={styles.logoImg} />
          <span className={styles.logoTitle}>Acceso al Dashboard STEM</span>
          <span className={styles.logoSub}>Ecosistema STEM — Ciudad Juárez</span>
        </div>

        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.fieldGroup}>
            <label className={styles.label} htmlFor="username">Usuario</label>
            <input
              id="username"
              className={styles.input}
              type="text"
              autoComplete="username"
              placeholder="Nombre de usuario"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div className={styles.fieldGroup}>
            <label className={styles.label} htmlFor="password">Contraseña</label>
            <input
              id="password"
              className={styles.input}
              type="password"
              autoComplete="current-password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && <p className={styles.error}>{error}</p>}

          <button className={styles.submitBtn} type="submit" disabled={loading}>
            {loading ? 'Iniciando sesión...' : 'Iniciar sesión'}
          </button>
        </form>
      </div>
    </div>
  );
}
