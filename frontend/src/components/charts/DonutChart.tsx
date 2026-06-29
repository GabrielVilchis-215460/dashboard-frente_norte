// -- Gráfica de dona --

import { useRef, useState, useEffect } from 'react';
import {
  PieChart, Pie, Cell, Legend, ResponsiveContainer, Tooltip,
} from 'recharts';
import { Skeleton } from '../ui';
import styles from './DonutChart.module.css';

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
  const wrapperRef = useRef<HTMLDivElement>(null);
  const [colors, setColors] = useState<string[]>(FALLBACK);

  useEffect(() => {
    setColors(readThemeColors(wrapperRef.current));
  }, [loading, data]);

  if (loading) return <Skeleton width="100%" height="220px" borderRadius="12px" />;
  if (!data.length) return <p className={styles.empty}>Sin datos disponibles</p>;

  return (
    <div className={styles.wrapper} ref={wrapperRef}>
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
              <Cell key={i} fill={colors[i % colors.length]} stroke="transparent" />
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
