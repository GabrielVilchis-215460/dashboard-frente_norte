// Tipos de actividades ofrecidas

import {
  IconTools,
  IconMicrophone,
  IconSchool,
  IconRocket,
  IconActivity,
} from '@tabler/icons-react';
import { Skeleton } from '../../../components/ui';
import styles from './ActivityCards.module.css';

interface Props {
  actividades: Record<string, number>;
  loading: boolean;
}

// Asigna un icono según palabras clave del nombre de la categoría
function pickIcon(label: string): React.ComponentType<{ size?: number; stroke?: number }> {
  const l = label.toLowerCase();
  if (l.includes('taller') || l.includes('curso') || l.includes('bootcamp')) return IconTools;
  if (l.includes('evento') || l.includes('conferencia')) return IconMicrophone;
  if (l.includes('mentor') || l.includes('largo plazo')) return IconSchool;
  if (l.includes('incuba') || l.includes('acelera')) return IconRocket;
  return IconActivity;
}

export function ActivityCards({ actividades, loading }: Props) {
  if (loading) {
    return (
      <div className={styles.grid}>
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className={styles.skeletonCard}>
            <Skeleton width="40px" height="32px" />
            <Skeleton width="32px" height="32px" borderRadius="8px" />
            <Skeleton width="80%" height="14px" />
          </div>
        ))}
      </div>
    );
  }

  const entries = Object.entries(actividades);

  if (!entries.length) {
    return <p className={styles.empty}>Sin datos disponibles</p>;
  }

  return (
    <div className={styles.grid}>
      {entries.map(([label, count], i) => {
        const Icon = pickIcon(label);
        return (
          <div
            key={label}
            className={`${styles.card} animate-fade-in-up`}
            style={{ animationDelay: `${i * 70}ms` }}
          >
            <span className={styles.count}>{count}</span>
            <div className={styles.iconWrap}>
              <Icon size={26} stroke={1.5} />
            </div>
            <span className={styles.label}>{label}</span>
          </div>
        );
      })}
    </div>
  );
}