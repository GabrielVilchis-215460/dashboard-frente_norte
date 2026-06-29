// -- Gráfica de barras horizontales --

import { useRef, useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell,
} from 'recharts';
import { Skeleton } from '../ui';
import styles from './HorizontalBarChart.module.css';

const FALLBACK = ['#60a5fa', '#34d399', '#a78bfa', '#f472b6'];

function readThemeColors(node: HTMLElement | null): string[] {
  const el = node ?? document.documentElement;
  const style = getComputedStyle(el);
  return [
    style.getPropertyValue('--accent-a').trim() || FALLBACK[0],
    style.getPropertyValue('--accent-b').trim() || FALLBACK[1],
    style.getPropertyValue('--accent-c').trim() || FALLBACK[2],
    style.getPropertyValue('--accent-d').trim() || FALLBACK[3],
  ];
}

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
  const wrapperRef = useRef<HTMLDivElement>(null);
  const [colors, setColors] = useState<string[]>(FALLBACK);

  useEffect(() => {
    setColors(readThemeColors(wrapperRef.current));
  }, [loading, data]);

  if (loading) return <Skeleton width="100%" height="220px" borderRadius="12px" />;
  if (!data.length) return <p className={styles.empty}>Sin datos disponibles</p>;

  return (
    <div
      className={styles.wrapper}
      ref={wrapperRef}
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
                fill={singleColor ? colors[0] : colors[i % colors.length]}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
