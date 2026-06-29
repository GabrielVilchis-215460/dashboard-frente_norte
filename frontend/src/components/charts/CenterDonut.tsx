// Donut con valor central

import { useRef, useState, useEffect } from 'react';
import {
  PieChart, Pie, Cell, ResponsiveContainer,
} from 'recharts';
import { Skeleton } from '../ui';
import styles from './CenterDonut.module.css';

const FALLBACK = ['#38bdf8', '#7dd3fc'];

function readThemeColors(node: HTMLElement | null): string[] {
  const el = node ?? document.documentElement;
  const style = getComputedStyle(el);
  return [
    style.getPropertyValue('--accent-a').trim() || FALLBACK[0],
    style.getPropertyValue('--accent-b').trim() || FALLBACK[1],
  ];
}

interface Props {
  value: number;
  centerLabel?: string;
  legendA?: string;
  legendB?: string;
  loading?: boolean;
}

export function CenterDonut({
  value,
  centerLabel,
  legendA = 'Mujeres',
  legendB = 'Hombres',
  loading = false,
}: Props) {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const [colors, setColors] = useState<string[]>(FALLBACK);

  useEffect(() => {
    setColors(readThemeColors(wrapperRef.current));
  }, [loading, value]);

  if (loading) return <Skeleton width="100%" height="220px" borderRadius="12px" />;

  const data = [
    { name: legendA, value },
    { name: legendB, value: Math.max(0, 100 - value) },
  ];

  return (
    <div className={styles.wrapper} ref={wrapperRef}>
      <div className={styles.chartArea}>
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={64}
              outerRadius={88}
              paddingAngle={2}
              dataKey="value"
              startAngle={90}
              endAngle={-270}
              animationDuration={600}
            >
              <Cell fill={colors[0]} stroke="transparent" />
              <Cell fill={colors[1]} stroke="transparent" />
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className={styles.center}>
          <span className={styles.value}>{centerLabel ?? `${value}%`}</span>
        </div>
      </div>

      <div className={styles.legend}>
        <span className={styles.legendItem}>
          <span className={styles.dot} style={{ background: colors[1] }} />
          {legendB}
        </span>
        <span className={styles.legendItem}>
          <span className={styles.dot} style={{ background: colors[0] }} />
          {legendA}
        </span>
      </div>
    </div>
  );
}