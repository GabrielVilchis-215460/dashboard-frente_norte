// -- Gráfica de dona --

import {
  PieChart, Pie, Cell, Legend, ResponsiveContainer, Tooltip,
} from 'recharts';
import { Skeleton } from '../ui';
import styles from './DonutChart.module.css';

// Los colores se leen en runtime desde las CSS vars del tema
function getThemeColors(): string[] {
  const el = document.documentElement;
  const style = getComputedStyle(el);
  return [
    style.getPropertyValue('--accent-a').trim() || '#60a5fa',
    style.getPropertyValue('--accent-b').trim() || '#34d399',
    style.getPropertyValue('--accent-c').trim() || '#a78bfa',
    style.getPropertyValue('--accent-d').trim() || '#f472b6',
  ];
}

interface DataPoint { name: string; value: number; }
interface Props { data: DataPoint[]; loading?: boolean; }

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className={styles.tooltip}>
      <span className={styles.tooltipName}>{payload[0].name}</span>
      <span className={styles.tooltipValue}>{payload[0].value}</span>
    </div>
  );
}

export function DonutChart({ data, loading = false }: Props) {
  if (loading) return <Skeleton width="100%" height="220px" borderRadius="12px" />;
  if (!data.length) return <p className={styles.empty}>Sin datos disponibles</p>;

  const COLORS = getThemeColors();

  return (
    <div className={styles.wrapper}>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            cx="35%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={3}
            dataKey="value"
            animationBegin={0}
            animationDuration={600}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} stroke="transparent" />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            layout="vertical"
            align="right"
            verticalAlign="middle"
            iconType="circle"
            iconSize={8}
            formatter={(value) => (
              <span className={styles.legendLabel}>{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
