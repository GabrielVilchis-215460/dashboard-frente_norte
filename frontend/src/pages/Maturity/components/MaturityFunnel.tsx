// Barras horizontales y bloques de detalle
// ANTERIOR: Embudo + bloques de detalle <- Depricated

import { useState } from 'react';
import {
  IconRocket,
  IconPlant,
  IconTrendingUp,
} from '@tabler/icons-react';
import { Skeleton } from '../../../components/ui';
import { STAGES, normalizeStage } from './stageConfig';
import type { MadurezResponse } from '../../../types';
import styles from './MaturityFunnel.module.css';

const ICON_MAP: Record<string, React.ComponentType<any>> = {
  IconRocket,
  IconPlant,
  IconTrendingUp,
};

interface Props {
  data?: MadurezResponse;
  loading: boolean;
}

function labelProgramas(n: number): string {
  return n === 1 ? 'programa' : 'programas';
}

export function MaturityFunnel({ data, loading }: Props) {
  const [hovered, setHovered] = useState<number | null>(null);
 
  if (loading) {
    return (
      <div className={styles.layout}>
        <div className={styles.cardsCol}>
          {STAGES.map((s) => (
            <Skeleton key={s.key} width="100%" height="100px" borderRadius="12px" />
          ))}
        </div>
        <div className={styles.chartCol}>
          {STAGES.map((s) => (
            <Skeleton key={s.key} width="100%" height="100px" borderRadius="12px" />
          ))}
        </div>
      </div>
    );
  }
 
  // Datos por etapa en el orden forzado
  const stageData = STAGES.map((stage) => {
    const programasEntry = Object.entries(data?.por_etapa ?? {}).find(
      ([k]) => normalizeStage(k) === stage.key
    );
    const beneficiariosEntry = Object.entries(data?.beneficiarios_por_etapa ?? {}).find(
      ([k]) => normalizeStage(k) === stage.key
    );
    return {
      ...stage,
      programas: programasEntry?.[1] ?? 0,
      beneficiarios: beneficiariosEntry?.[1] ?? 0,
    };
  });
 
  const maxProgramas = Math.max(1, ...stageData.map((s) => s.programas));
 
  return (
    <div className={styles.layout}>
      {/* Tarjetas de detalle */}
      <div className={styles.cardsCol}>
        {stageData.map((stage, i) => {
          const Icon = ICON_MAP[stage.icon];
          const isDimmed = hovered !== null && hovered !== i;
          const isActive = hovered === i;
          return (
            <div
              key={stage.key}
              className={`${styles.detailBlock} ${isActive ? styles.detailBlockActive : ''} animate-fade-in-up`}
              style={{ animationDelay: `${i * 80}ms`, opacity: isDimmed ? 0.55 : 1 }}
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
            >
              <div className={styles.detailHeader}>
                <span className={styles.detailIcon} style={{ color: stage.color }}>
                  {Icon && <Icon size={20} stroke={1.8} />}
                </span>
                <h4 className={styles.detailTitle}>{stage.label}</h4>
              </div>

              <div className={styles.metrics}>
                <div className={styles.metric}>
                  <span className={styles.metricValue} style={{ color: stage.color }}>
                    {stage.programas}
                  </span>
                  <span className={styles.metricLabel}>{labelProgramas(stage.programas)}</span>
                </div>
                <div className={styles.metric}>
                  <span className={styles.metricValue} style={{ color: stage.color }}>
                    {stage.beneficiarios.toLocaleString('es-MX')}
                  </span>
                  <span className={styles.metricLabel}>beneficiarios</span>
                </div>
              </div>

              <p className={styles.detailDesc}>{stage.description}</p>
            </div>
          );
        })}
      </div>
 
      {/* Gráfica de barras */}
      <div className={styles.chartCol}>
        {stageData.map((stage, i) => {
          const pct = Math.max(4, Math.round((stage.programas / maxProgramas) * 100));
          const isDimmed = hovered !== null && hovered !== i;
          return (
            <div
              key={stage.key}
              className={styles.barRow}
              style={{ opacity: isDimmed ? 0.4 : 1 }}
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
            >
              <span className={styles.barRowLabel}>{stage.label}</span>

              <div className={styles.barTrack}>
                <div
                  className={`${styles.barFill} animate-fade-in`}
                  style={{
                    width: `${pct}%`,
                    background: stage.funnelColor,
                    animationDelay: `${i * 120}ms`,
                    filter: hovered === i ? 'brightness(1.15)' : undefined,
                  }}
                />
              </div>

              <div className={styles.barRowValues}>
                <span style={{ color: stage.color }}>
                  <strong>{stage.programas}</strong> {labelProgramas(stage.programas)}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}