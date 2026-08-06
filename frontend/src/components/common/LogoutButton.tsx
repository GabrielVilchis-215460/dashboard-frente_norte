import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { IconLogout } from '@tabler/icons-react';
import { authStorage } from '../../services/adminApi';
import { ROUTES } from '../../constants/routes';
import { ConfirmDialog } from './ConfirmDialog';
import styles from './LogoutButton.module.css';

interface Props {
  /** Muestra el texto junto al ícono. Default: false (solo ícono). */
  showLabel?: boolean;
  className?: string;
}

export function LogoutButton({ showLabel = false, className = '' }: Props) {
  const navigate = useNavigate();
  const [confirmando, setConfirmando] = useState(false);

  function confirmarLogout() {
    authStorage.clearAll();
    navigate(ROUTES.LOGIN, { replace: true });
  }

  return (
    <>
      <button
        type="button"
        className={`${styles.btn} ${className}`}
        onClick={() => setConfirmando(true)}
        aria-label="Cerrar sesión"
      >
        <IconLogout size={16} stroke={1.5} />
        {showLabel && <span>Cerrar sesión</span>}
      </button>

      {confirmando && (
        <ConfirmDialog
          title="¿Cerrar sesión?"
          message="Vas a salir de tu sesión actual. Tendrás que volver a iniciar sesión para acceder al dashboard."
          confirmLabel="Cerrar sesión"
          cancelLabel="Cancelar"
          danger
          onConfirm={confirmarLogout}
          onCancel={() => setConfirmando(false)}
        />
      )}
    </>
  );
}