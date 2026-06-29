// -- Gráfica de barras horizontales --

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  Cell,
} from 'recharts';
import { Skeleton } from '../ui';
import styles from './HorizontalBarChart.module.css';

const GRADIENT_COLORS = [
  '#2dd4bf',
  '#3b82f6',
  '#0891b2',
  '#10b981',
  '#6366f1',
];

interface DataPoint {
  name: string;
  value: number;
}

interface Props {
  data: DataPoint[];
  loading?: boolean;
  color?: string;
}

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className={styles.tooltip}>
      <span className={styles.tooltipName}>{label}</span>
      <span className={styles.tooltipValue}>{payload[0].value}</span>
    </div>
  );
}

export function HorizontalBarChart({ data, loading = false, color }: Props) {
  if (loading) {
    return <Skeleton width="100%" height="220px" borderRadius="12px" />;
  }

  if (!data.length) {
    return <p className={styles.empty}>Sin datos disponibles</p>;
  }

  return (
    <div className={styles.wrapper}>
      <ResponsiveContainer width="100%" height={Math.max(data.length * 40, 160)}>
        <BarChart
          layout="vertical"
          data={data}
          margin={{ top: 0, right: 32, bottom: 0, left: 0 }}
        >
          <XAxis type="number" hide />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fill: 'var(--color-text-secondary)', fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            width={110}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]} animationDuration={600}>
            {data.map((_, index) => (
              <Cell
                key={index}
                fill={color ?? GRADIENT_COLORS[index % GRADIENT_COLORS.length]}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
