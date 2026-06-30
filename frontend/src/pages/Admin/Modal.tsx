import { ReactNode, useEffect } from 'react';
import styles from './Modal.module.css';

interface ModalProps {
  title: string;
  onClose: () => void;
  onConfirm?: () => void;
  confirmLabel?: string;
  loading?: boolean;
  children: ReactNode;
}

export function Modal({ title, onClose, onConfirm, confirmLabel = 'Guardar', loading, children }: ModalProps) {
  // Cerrar con Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onClose]);

  return (
    <div className={styles.overlay} onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className={styles.modal}>
        <div className={styles.header}>
          <span className={styles.title}>{title}</span>
          <button className={styles.closeBtn} onClick={onClose} aria-label="Cerrar">✕</button>
        </div>
        <div className={styles.body}>{children}</div>
        {onConfirm && (
          <div className={styles.footer}>
            <button className={styles.btnSecondary} onClick={onClose}>Cancelar</button>
            <button className={styles.btnPrimary} onClick={onConfirm} disabled={loading}>
              {loading ? 'Guardando...' : confirmLabel}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
