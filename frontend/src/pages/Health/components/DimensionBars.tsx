// Barras de dimensiones del ISE (escala 0-100)

import {
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell, LabelList,
} from 'recharts';
import { Skeleton } from '../../../components/ui';
import type { DimensionISE } from '../../../types';
import styles from './DimensionBars.module.css';

const DIM_COLORS = ['#34d3ab', '#34c8d3', '#60bcfa', '#59a4fa', '#7086ff'];

interface Props {
  dimensiones: DimensionISE[];
  loading: boolean;
}

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className={styles.tooltip}>
      <span className={styles.tooltipName}>{label}</span>
      <span className={styles.tooltipValue}>{payload[0].value.toFixed(1)} / 100</span>
    </div>
  );
}

export function DimensionBars({ dimensiones, loading }: Props) {
  if (loading) {
    return <Skeleton width="100%" height="320px" borderRadius="12px" />;
  }

  if (!dimensiones.length) {
    return <p className={styles.empty}>Sin datos disponibles</p>;
  }

  const data = dimensiones.map((d) => ({
    name: d.nombre,
    value: d.score,
  }));

  return (
    <div className={styles.wrapper}>
      <ResponsiveContainer width="100%" height={Math.max(data.length * 56, 280)}>
        <BarChart
          layout="vertical"
          data={data}
          margin={{ top: 10, right: 40, bottom: 0, left: 0 }}
          barCategoryGap="28%"
        >
          <XAxis
            type="number"
            domain={[0, 100]}
            ticks={[0, 20, 40, 60, 80, 100]}
            tick={{ fill: 'rgba(255,255,255,0.60)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            orientation="top"
          />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fill: 'rgba(255,255,255,0.80)', fontSize: 12, fontFamily: 'Inter, sans-serif' }}
            axisLine={false}
            tickLine={false}
            width={150}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
          <Bar dataKey="value" radius={[0, 6, 6, 0]} animationDuration={700} barSize={16}>
            {data.map((_, i) => (
              <Cell key={i} fill={DIM_COLORS[i % DIM_COLORS.length]} />
            ))}
            <LabelList
              dataKey="value"
              position="right"
              formatter={(v: number) => v.toFixed(1).replace(/\.0$/, '')}
              fill="rgba(255,255,255,0.80)"
              fontSize={12}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}