// Gráfica de área del histórico trimestral

import { useRef, useState, useEffect } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Skeleton } from '../../../components/ui';
import type { HistoricoTrimestralItem } from '../../../types';
import styles from './EventsAreaChart.module.css';

interface Props {
  data: HistoricoTrimestralItem[];
  loading: boolean;
}

const FALLBACK_COLOR = '#34d399';

function readAccent(node: HTMLElement | null): string {
  const el = node ?? document.documentElement;
  return getComputedStyle(el).getPropertyValue('--accent-a').trim() || FALLBACK_COLOR;
}

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className={styles.tooltip}>
      <span className={styles.tooltipLabel}>{label}</span>
      <span className={styles.tooltipValue}>{payload[0].value} eventos</span>
    </div>
  );
}

export function EventsAreaChart({ data, loading }: Props) {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const [color, setColor] = useState(FALLBACK_COLOR);

  useEffect(() => {
    setColor(readAccent(wrapperRef.current));
  }, [loading, data]);

  if (loading) return <Skeleton width="100%" height="240px" borderRadius="12px" />;
  if (!data.length) return <p className={styles.empty}>Sin datos disponibles</p>;

  const gradId = 'events-area-grad';

  return (
    <div className={styles.wrapper} ref={wrapperRef}>
      <ResponsiveContainer width="100%" height={240}>
        <AreaChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: -16 }}>
          <defs>
            <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor={color} stopOpacity={0.4} />
              <stop offset="95%" stopColor={color} stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="rgba(255,255,255,0.07)"
            vertical={false}
          />
          <XAxis
            dataKey="trimestre"
            tick={{ fill: 'rgba(255,255,255,0.50)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            allowDecimals={false}
            tick={{ fill: 'rgba(255,255,255,0.50)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="eventos"
            stroke={color}
            strokeWidth={2.5}
            fill={`url(#${gradId})`}
            dot={{ fill: color, r: 4, strokeWidth: 0 }}
            activeDot={{ r: 6, strokeWidth: 0 }}
            animationDuration={700}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}