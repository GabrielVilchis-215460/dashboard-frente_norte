// -- Placeholder para estados de carga --

import styles from './Skeleton.module.css';

interface SkeletonProps {
  width?: string;
  height?: string;
  borderRadius?: string;
  className?: string;
  style?: React.CSSProperties;
}

export function Skeleton({
  width = '100%',
  height = '1rem',
  borderRadius = '6px',
  className = '',
  style, 
}: SkeletonProps) {
  return (
    <div
      className={`${styles.skeleton} ${className}`}
      style={{ width, height, borderRadius, ...style }}
      aria-hidden="true"
    />
  );
}

export function SkeletonKPI() {
  return (
    <div className={styles.kpiSkeleton}>
      <Skeleton width="40%" height="14px" />
      <Skeleton width="60%" height="36px" />
      <Skeleton width="80%" height="12px" />
    </div>
  );
}
