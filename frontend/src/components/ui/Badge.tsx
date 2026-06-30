// -- Etiqueta de categoría o estado --

import styles from './Badge.module.css';

type BadgeVariant = 'default' | 'cyan' | 'green' | 'blue' | 'warning';

interface BadgeProps {
  label: string;
  variant?: BadgeVariant;
}

export function Badge({ label, variant = 'default' }: BadgeProps) {
  return (
    <span className={`${styles.badge} ${styles[variant]}`}>
      {label}
    </span>
  );
}
