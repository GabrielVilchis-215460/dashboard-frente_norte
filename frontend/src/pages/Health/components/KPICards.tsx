import { useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { IconTrendingUp, IconTrendingDown, IconMinus } from '@tabler/icons-react';
import { Skeleton } from '../../../components/ui';
import type { KPIIndicador } from '../../../types';
import styles from './KPICards.module.css';

interface Props {
  kpis: KPIIndicador[];
  loading: boolean;
}

const KPI_INFO: Record<string, string> = {
  egresados_stem: 'Porcentaje de egresados en areas STEM (% sobre el total de egresados).',
  mujeres_stem: 'Porcentaje de mujeres en egreso de areas STEM (% sobre egresados).',
  empleo_stem: 'Porcentaje de empleo en areas STEM (% de empleos formales).',
  salario_stem: 'Salario promedio en ocupaciones STEM.',
  centros_investigacion: 'Centros de investigación por 100k PEA.',
};

const EDGE_PADDING = 12;

function formatConUnidad(valor: number, unidad: string, clave: string): string {
  const v = valor.toLocaleString('es-MX', { maximumFractionDigits: 1 });
  const prefijo = clave === 'salario_stem' ? '$' : '';
  return unidad.trim() === '%' ? `${prefijo}${v}%` : `${prefijo}${v} ${unidad}`;
}

// Diferencia puntual
function formatDelta(delta: number, unidad: string, clave: string): string {
  const signo = delta > 0 ? '+' : '';
  return `${signo}${formatConUnidad(delta, unidad, clave)}`;
}

interface ItemProps {
  kpi: KPIIndicador;
}

function KPICardItem({ kpi }: ItemProps) {
  const [open, setOpen] = useState(false);
  const [pos, setPos] = useState({ top: 0, left: 0, width: 0 });
  const cardRef = useRef<HTMLDivElement>(null);

  const cambio = kpi.cambio_porcentual; // ahora es diferencia directa, no %
  const esPositivo = cambio !== null && cambio > 0;
  const esNegativo = cambio !== null && cambio < 0;

  function handleEnter() {
    const rect = cardRef.current?.getBoundingClientRect();
    if (rect) {
      const left = Math.min(
        Math.max(rect.left, EDGE_PADDING),
        window.innerWidth - rect.width - EDGE_PADDING
      );
      setPos({ top: rect.bottom + 8, left, width: rect.width });
    }
    setOpen(true);
  }

  return (
    <div
      ref={cardRef}
      className={styles.card}
      onMouseEnter={handleEnter}
      onMouseLeave={() => setOpen(false)}
    >
      <span className={styles.label}>{kpi.nombre}</span>
      <span className={styles.value}>{formatConUnidad(kpi.valor_actual, kpi.unidad, kpi.clave)}</span>

      <span
        className={`${styles.badge} ${
          esPositivo ? styles.badgeUp : esNegativo ? styles.badgeDown : styles.badgeNeutral
        }`}
      >
        {esPositivo && <IconTrendingUp size={12} stroke={2} />}
        {esNegativo && <IconTrendingDown size={12} stroke={2} />}
        {cambio === null && <IconMinus size={12} stroke={2} />}
        {cambio !== null ? formatDelta(cambio, kpi.unidad, kpi.clave) : 'Sin cambio'}
      </span>

      {open &&
        createPortal(
          <div
            className={styles.popover}
            style={{ top: pos.top, left: pos.left, width: pos.width }}
          >
            {KPI_INFO[kpi.clave] ?? `Información contextual pendiente para "${kpi.nombre}".`}
          </div>,
          document.body
        )}
    </div>
  );
}

export function KPICards({ kpis, loading }: Props) {
  if (loading) {
    return (
      <div className={styles.grid}>
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} width="100%" height="110px" borderRadius="12px" />
        ))}
      </div>
    );
  }

  return (
    <div className={styles.grid}>
      {kpis.map((k) => (
        <KPICardItem key={k.clave} kpi={k} />
      ))}
    </div>
  );
}