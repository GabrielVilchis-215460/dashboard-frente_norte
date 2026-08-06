import { createPortal } from 'react-dom';
import styles from './ConfirmDialog.module.css';

interface Props {
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  danger?: boolean;
}

export function ConfirmDialog({
  title,
  message,
  confirmLabel = 'Confirmar',
  cancelLabel = 'Cancelar',
  onConfirm,
  onCancel,
  danger = false,
}: Props) {
  return createPortal(
    <div className={styles.overlay} onClick={onCancel}>
      <div className={styles.card} onClick={(e) => e.stopPropagation()}>
        <h3 className={styles.title}>{title}</h3>
        <p className={styles.message}>{message}</p>
        <div className={styles.actions}>
          <button type="button" className={styles.cancelBtn} onClick={onCancel}>
            {cancelLabel}
          </button>
          <button
            type="button"
            className={danger ? styles.confirmBtnDanger : styles.confirmBtn}
            onClick={onConfirm}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}