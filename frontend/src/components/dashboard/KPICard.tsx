// KPICard: Tarjeta de indicador clave (num + descripción)

import React from 'react';
import { SkeletonKPI } from '../ui/Skeleton';
import { useMinDuration } from '../../hooks/useMinDuration';
import styles from './KPICard.module.css';

interface BadgeProps {
  value: number;
  positive: boolean;
}

interface KPICardProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  loading?: boolean;
  animationDelay?: number;
  badge?: BadgeProps;
}

export function KPICard({
  label,
  value,
  icon,
  loading = false,
  animationDelay = 0,
  badge,
}: KPICardProps) {
  const showLoading = useMinDuration(loading, 250);
  if (showLoading) {
    return (
      <div className={styles.card}>
        <SkeletonKPI />
      </div>
    );
  }

  return (
    <div
      className={`${styles.card} animate-fade-in-up`}
      style={{ animationDelay: `${animationDelay}ms` }}
    >
      <div className={styles.inner}>
        <div className={styles.textGroup}>
          <div className={styles.valueRow}>
            <span className={styles.value}>{value}</span>
            {badge && (
              <span className={`${styles.badge} ${badge.positive ? styles.badgePos : styles.badgeNeg}`}>
                {badge.positive ? `▲ ${badge.value}` : `▼ ${Math.abs(badge.value)}`}
              </span>
            )}
          </div>
          <span className={styles.label}>{label}</span>
        </div>
        {icon && (
          <div className={styles.iconWrap} aria-hidden="true">
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
