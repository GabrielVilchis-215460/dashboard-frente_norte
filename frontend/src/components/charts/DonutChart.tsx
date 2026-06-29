// -- Gráfica de dona --

import {
  PieChart,
  Pie,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { Skeleton } from '../ui';
import styles from './DonutChart.module.css';

const COLORS = [
  '#2dd4bf', // cyan
  '#3b82f6', // blue
  '#10b981', // green
  '#0891b2', // teal oscuro
  '#6366f1', // indigo
  '#8b5cf6', // violet
];

interface DataPoint {
  name: string;
  value: number;
}

interface Props {
  data: DataPoint[];
  loading?: boolean;
}

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
  if (loading) {
    return <Skeleton width="100%" height="220px" borderRadius="12px" />;
  }

  if (!data.length) {
    return <p className={styles.empty}>Sin datos disponibles</p>;
  }

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
            {data.map((_, index) => (
              <Cell
                key={index}
                fill={COLORS[index % COLORS.length]}
                stroke="transparent"
              />
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
