import { useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip,
} from 'recharts';
import { IconChevronLeft, IconChevronRight } from '@tabler/icons-react';
import { Skeleton } from '../../../components/ui';
import type { SlideEvolucionIndicador } from '../../../types';
import styles from './EvolutionCarousel.module.css';

interface Props {
  slides: SlideEvolucionIndicador[];
  loading: boolean;
}

function formatConUnidad(valor: number, unidad: string, clave: string): string {
  const v = valor.toLocaleString('es-MX', { maximumFractionDigits: 1 });
  const prefijo = clave === 'salario_stem' ? '$' : '';
  return unidad.trim() === '%' ? `${prefijo}${v}%` : `${prefijo}${v} ${unidad}`;
}

function CustomTooltip({ active, payload, label, unidad, clave }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className={styles.tooltip}>
      <span className={styles.tooltipName}>{label}</span>
      <span className={styles.tooltipValue}>{formatConUnidad(payload[0].value, unidad, clave)}</span>
    </div>
  );
}

export function EvolutionCarousel({ slides, loading }: Props) {
  const [index, setIndex] = useState(0);

  if (loading) {
    return <Skeleton width="100%" height="280px" borderRadius="12px" />;
  }

  if (!slides.length) {
    return <p className={styles.empty}>Sin datos disponibles</p>;
  }

  const total = slides.length;
  const slide = slides[index];
  const data = slide.serie_historica.map((p) => ({ anio: p.anio, valor: p.valor }));

  const prev = () => setIndex((i) => (i - 1 + total) % total);
  const next = () => setIndex((i) => (i + 1) % total);

  return (
    <div className={styles.wrapper}>
      <div className={styles.divider} />

      <div className={styles.header}>
        <span className={styles.title}>
          {slide.indicador_nombre} <span className={styles.titleUnit}>({slide.unidad})</span>
        </span>
        <div className={styles.nav}>
          <button className={styles.navBtn} onClick={prev} aria-label="Anterior">
            <IconChevronLeft size={16} stroke={1.8} />
          </button>
          <span className={styles.counter}>{index + 1}/{total}</span>
          <button className={styles.navBtn} onClick={next} aria-label="Siguiente">
            <IconChevronRight size={16} stroke={1.8} />
          </button>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={data} margin={{ top: 10, right: 16, bottom: 0, left: -16 }}>
          <XAxis
            dataKey="anio"
            tick={{ fill: 'rgba(255,255,255,0.60)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: 'rgba(255,255,255,0.60)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={40}
          />
          <Tooltip
            content={(props) => <CustomTooltip {...props} unidad={slide.unidad} clave={slide.indicador_clave} />}
            cursor={{ stroke: 'var(--glass-border)' }}
          />
          <Line
            type="monotone"
            dataKey="valor"
            stroke="var(--accent-a)"
            strokeWidth={2.5}
            dot={{ r: 4, fill: 'var(--accent-a)', strokeWidth: 0 }}
            activeDot={{ r: 6 }}
            animationDuration={700}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}