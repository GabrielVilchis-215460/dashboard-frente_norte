// -- Gráfica de barras horizontales --

import {
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell,
} from 'recharts';
import { Skeleton } from '../ui';
import styles from './HorizontalBarChart.module.css';

// Paleta combinada de los 3 temas del sistema: navy, teal y cyan
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
interface Props {
  data: DataPoint[];
  loading?: boolean;
  singleColor?: boolean;
  /** Si true, el gráfico llena el alto del contenedor en vez de altura fija */
  fillHeight?: boolean;
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

export function HorizontalBarChart({ data, loading = false, singleColor = false, fillHeight = false }: Props) {
  if (loading) return <Skeleton width="100%" height="220px" borderRadius="12px" />;
  if (!data.length) return <p className={styles.empty}>Sin datos disponibles</p>;

  return (
    <div
      className={styles.wrapper}
      style={fillHeight ? { height: '100%' } : undefined}
    >
      <ResponsiveContainer
        width="100%"
        height={fillHeight ? '100%' : Math.max(data.length * 40, 160)}
      >
        <BarChart
          layout="vertical"
          data={data}
          margin={{ top: 0, right: 36, bottom: 0, left: 0 }}
          barCategoryGap={fillHeight ? '28%' : '20%'}
        >
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
                fill={singleColor ? CHART_PALETTE[0] : CHART_PALETTE[i % CHART_PALETTE.length]}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
