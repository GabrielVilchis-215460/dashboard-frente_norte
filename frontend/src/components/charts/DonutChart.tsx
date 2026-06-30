// -- Gráfica de dona --

import {
  PieChart, Pie, Cell, Legend, ResponsiveContainer, Tooltip,
} from 'recharts';
import { Skeleton } from '../ui';
import styles from './DonutChart.module.css';

// Paleta combinada de los 3 temas del sistema: navy, teal y cyan
// Garantiza contraste visual independientemente del tema activo
const CHART_PALETTE = [
  '#60a5fa', // navy accent-a   (azul)
  '#2dd4bf', // teal accent-a   (verde agua)
  '#38bdf8', // cyan accent-a   (celeste)
  '#93c5fd', // navy accent-b   (azul claro)
  '#5eead4', // teal accent-b   (menta)
  '#818cf8', // acento complementario (morado)
  '#34d399', // acento complementario (esmeralda)
  '#3b82f6', // navy accent-c   (azul saturado)
];

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
              <Cell key={i} fill={CHART_PALETTE[i % CHART_PALETTE.length]} stroke="transparent" />
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
