// Embudo + bloques de detalle

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

// Geometría del embudo (viewBox 300 x 360)
const VB_W = 300;
const VB_H = 360;
const SEG_H = VB_H / 3;     // alto de cada segmento
const GAP = 6;
const TOP_W = 280;          // ancho superior (primer segmento)
const BOTTOM_W = 120;       // ancho inferior (último segmento)

// Ancho interpolado en una altura dada
function widthAt(y: number): number {
  const t = y / VB_H;
  return TOP_W - (TOP_W - BOTTOM_W) * t;
}

// Genera los 4 puntos del trapecio del segmento
function trapezoidPoints(i: number): string {
  const yTop = i * SEG_H + GAP / 2;
  const yBot = (i + 1) * SEG_H - GAP / 2;
  const wTop = widthAt(yTop);
  const wBot = widthAt(yBot);
  const cx = VB_W / 2;

  const xTopL = cx - wTop / 2;
  const xTopR = cx + wTop / 2;
  const xBotL = cx - wBot / 2;
  const xBotR = cx + wBot / 2;

  return `${xTopL},${yTop} ${xTopR},${yTop} ${xBotR},${yBot} ${xBotL},${yBot}`;
}

export function MaturityFunnel({ data, loading }: Props) {
  const [hovered, setHovered] = useState<number | null>(null);

  if (loading) {
    return (
      <div className={styles.layout}>
        <Skeleton width="100%" height="360px" borderRadius="12px" />
        <div className={styles.details}>
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

  return (
    <div className={styles.layout}>
      {/* Embudo custom SVG */}
      <div className={styles.funnelWrap}>
        <svg
          viewBox={`0 0 ${VB_W} ${VB_H}`}
          className={styles.funnelSvg}
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            {stageData.map((s, i) => (
              <linearGradient
                key={i}
                id={`funnel-grad-${i}`}
                x1="0" y1="0" x2="0" y2="1"
              >
                <stop offset="0%" stopColor={s.funnelColor} stopOpacity="0.95" />
                <stop offset="100%" stopColor={s.funnelColor} stopOpacity="0.75" />
              </linearGradient>
            ))}
          </defs>

          {stageData.map((_, i) => (
            <polygon
              key={i}
              points={trapezoidPoints(i)}
              fill={`url(#funnel-grad-${i})`}
              className={styles.segment}
              style={{
                opacity: hovered === null || hovered === i ? 1 : 0.45,
              }}
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
            />
          ))}
        </svg>

        {/* Tooltip flotante en hover */}
        {hovered !== null && (
          <div className={styles.tooltip} style={{ borderColor: stageData[hovered].funnelColor }}>
            <span className={styles.tooltipTitle}>{stageData[hovered].label}</span>
            <span className={styles.tooltipRow}>
              <strong>{stageData[hovered].programas}</strong> programas
            </span>
            <span className={styles.tooltipRow}>
              <strong>{stageData[hovered].beneficiarios.toLocaleString('es-MX')}</strong> beneficiarios
            </span>
          </div>
        )}
      </div>

      {/* Bloques de detalle por etapa */}
      <div className={styles.details}>
        {stageData.map((stage, i) => {
          const Icon = ICON_MAP[stage.icon];
          return (
            <div
              key={stage.key}
              className={`${styles.detailBlock} animate-fade-in-up`}
              style={{ animationDelay: `${i * 80}ms` }}
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
            >
              <div className={styles.detailHeader}>
                <span className={styles.detailIcon} style={{ color: stage.color }}>
                  {Icon && <Icon size={20} stroke={1.5} />}
                </span>
                <h4 className={styles.detailTitle}>{stage.label}</h4>
              </div>

              <div className={styles.metrics}>
                <div className={styles.metric}>
                  <span className={styles.metricValue} style={{ color: stage.color }}>
                    {stage.programas}
                  </span>
                  <span className={styles.metricLabel}>programas</span>
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
    </div>
  );
}