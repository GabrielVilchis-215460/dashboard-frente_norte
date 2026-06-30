// Columnas de organizaciones por etapa de madurez

import {
  IconRocket,
  IconPlant,
  IconTrendingUp,
} from '@tabler/icons-react';
import { Skeleton } from '../../../components/ui';
import { STAGES, normalizeStage } from './stageConfig';
import type { MadurezDetalle } from '../../../types';
import styles from './OrgsByStage.module.css';

const ICON_MAP: Record<string, React.ComponentType<any>> = {
  IconRocket,
  IconPlant,
  IconTrendingUp,
};

interface Props {
  detalles: MadurezDetalle[];
  loading: boolean;
}

export function OrgsByStage({ detalles, loading }: Props) {
  if (loading) {
    return (
      <div className={styles.grid}>
        {STAGES.map((s) => (
          <Skeleton key={s.key} width="100%" height="180px" borderRadius="12px" />
        ))}
      </div>
    );
  }

  return (
    <div className={styles.grid}>
      {STAGES.map((stage, i) => {
        const Icon = ICON_MAP[stage.icon];
        // Busca el detalle del backend para esta etapa
        const detalle = detalles.find(
          (d) => normalizeStage(d.etapa) === stage.key
        );
        const orgs = detalle?.organizaciones ?? [];
        const count = detalle?.cantidad ?? 0;

        return (
          <div
            key={stage.key}
            className={`${styles.column} animate-fade-in-up`}
            style={{
              animationDelay: `${i * 80}ms`,
              borderColor: `${stage.color}40`,
            }}
          >
            <div className={styles.header}>
              <span className={styles.icon} style={{ color: stage.color }}>
                {Icon && <Icon size={22} stroke={1.5} />}
              </span>
              <h4 className={styles.title}>{stage.label}</h4>
              <span className={styles.count} style={{ color: stage.color }}>
                {count}
              </span>
            </div>

            <ul className={styles.orgList}>
              {orgs.length === 0 ? (
                <li className={styles.empty}>Sin organizaciones</li>
              ) : (
                orgs.map((org, idx) => (
                  <li key={idx} className={styles.orgItem}>
                    <span
                      className={styles.bullet}
                      style={{ background: stage.color }}
                    />
                    {org}
                  </li>
                ))
              )}
            </ul>
          </div>
        );
      })}
    </div>
  );
}