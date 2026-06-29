// -- Gráfica de barras horizontales --

import {
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell,
} from 'recharts';
import { Skeleton } from '../ui';
import styles from './HorizontalBarChart.module.css';

function getThemeColors(): string[] {
  const style = getComputedStyle(document.documentElement);
  return [
    style.getPropertyValue('--accent-a').trim() || '#60a5fa',
    style.getPropertyValue('--accent-b').trim() || '#34d399',
    style.getPropertyValue('--accent-c').trim() || '#a78bfa',
    style.getPropertyValue('--accent-d').trim() || '#f472b6',
  ];
}

interface DataPoint { name: string; value: number; }
interface Props { data: DataPoint[]; loading?: boolean; singleColor?: boolean; }

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className={styles.tooltip}>
      <span className={styles.tooltipName}>{label}</span>
      <span className={styles.tooltipValue}>{payload[0].value}</span>
    </div>
  );
}

export function HorizontalBarChart({ data, loading = false, singleColor = false }: Props) {
  if (loading) return <Skeleton width="100%" height="220px" borderRadius="12px" />;
  if (!data.length) return <p className={styles.empty}>Sin datos disponibles</p>;

  const COLORS = getThemeColors();

  return (
    <div className={styles.wrapper}>
      <ResponsiveContainer width="100%" height={Math.max(data.length * 40, 160)}>
        <BarChart layout="vertical" data={data} margin={{ top: 0, right: 36, bottom: 0, left: 0 }}>
          <XAxis type="number" hide />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fill: 'rgba(255,255,255,0.60)', fontSize: 12, fontFamily: 'Inter, sans-serif' }}
            axisLine={false}
            tickLine={false}
            width={120}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]} animationDuration={600}>
            {data.map((_, i) => (
              <Cell
                key={i}
                fill={singleColor ? COLORS[0] : COLORS[i % COLORS.length]}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
