// KPICard: Tarjeta de indicador clave (num + descripción)

import React from 'react';
import { SkeletonKPI } from '../ui/Skeleton';
import styles from './KPICard.module.css';

interface KPICardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  loading?: boolean;
  animationDelay?: number;
}

export function KPICard({
  label,
  value,
  icon,
  loading = false,
  animationDelay = 0,
}: KPICardProps) {
  if (loading) {
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
          <span className={styles.value}>{value}</span>
          <span className={styles.label}>{label}</span>
        </div>
        <div className={styles.iconWrap} aria-hidden="true">
          {icon}
        </div>
      </div>
    </div>
  );
}
