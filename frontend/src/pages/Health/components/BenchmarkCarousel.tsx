import { useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell,
} from 'recharts';
import { IconChevronLeft, IconChevronRight } from '@tabler/icons-react';
import { Skeleton } from '../../../components/ui';
import type { SlideBenchmarkIndicador } from '../../../types';
import styles from './BenchmarkCarousel.module.css';

interface Props {
  slides: SlideBenchmarkIndicador[];
  loading: boolean;
}

const OTROS_COLORS = ['#3d99e4', '#60bcfa', '#59a4fa', '#7eaef7'];

function formatConUnidad(valor: number, unidad: string, clave: string): string {
  const v = valor.toLocaleString('es-MX', { maximumFractionDigits: 1 });
  const prefijo = clave === 'salario_stem' ? '$' : '';
  return unidad.trim() === '%' ? `${prefijo}${v}%` : `${prefijo}${v} ${unidad}`;
}

function CustomTooltip({ active, payload, unidad, clave }: any) {
  if (!active || !payload?.length) return null;
  const p = payload[0].payload;
  return (
    <div className={styles.tooltip}>
      <span className={styles.tooltipName}>{p.ecosistema}</span>
      <span className={styles.tooltipValue}>{formatConUnidad(p.valor, unidad, clave)}</span>
    </div>
  );
}

export function BenchmarkCarousel({ slides, loading }: Props) {
  const [index, setIndex] = useState(0);

  if (loading) {
    return <Skeleton width="100%" height="280px" borderRadius="12px" />;
  }

  if (!slides.length) {
    return <p className={styles.empty}>Sin datos disponibles</p>;
  }

  const total = slides.length;
  const slide = slides[index];
  const data = slide.comparativa_ecosistemas.map((e) => ({
    ecosistema: e.ecosistema,
    valor: e.valor,
    esLocal: e.rol === 'local',
  }));

  let otroIdx = 0;

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

      <ResponsiveContainer width="100%" height={Math.max(data.length * 46, 220)}>
        <BarChart
          layout="vertical"
          data={data}
          margin={{ top: 10, right: 24, bottom: 0, left: 0 }}
          barCategoryGap="30%"
        >
          <XAxis
            type="number"
            tick={{ fill: 'rgba(255,255,255,0.60)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="ecosistema"
            tick={{ fill: 'rgba(255,255,255,0.80)', fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            width={110}
          />
          <Tooltip
            content={(props) => <CustomTooltip {...props} unidad={slide.unidad} clave={slide.indicador_clave} />}
            cursor={{ fill: 'rgba(255,255,255,0.05)' }}
          />
          <Bar dataKey="valor" radius={[0, 6, 6, 0]} barSize={16} animationDuration={700}>
            {data.map((d, i) => {
              const color = d.esLocal ? '#3cedfa' : OTROS_COLORS[otroIdx++ % OTROS_COLORS.length];
              return <Cell key={i} fill={color} />;
            })}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}