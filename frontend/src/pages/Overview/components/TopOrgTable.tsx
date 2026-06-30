// -- TopOrgTable: Ranking de organizaciones por número de programas --

import { Skeleton } from '../../../components/ui';
import type { TopOrganizacion } from '../../../types';
import styles from './TopOrgTable.module.css';

interface Props {
  items: TopOrganizacion[];
  loading: boolean;
}

export function TopOrgTable({ items, loading }: Props) {
  if (loading) {
    return (
      <div className={styles.list}>
        {Array.from({ length: 7 }).map((_, i) => (
          <div key={i} className={styles.skeletonRow}>
            <Skeleton width="24px" height="24px" borderRadius="6px" />
            <Skeleton width="60%" height="14px" />
            <Skeleton width="20%" height="14px" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <ol className={styles.list}>
      {items.map((org, index) => (
        <li key={org.nombre} className={`${styles.row} animate-fade-in-up`} style={{ animationDelay: `${index * 50}ms` }}>
          <span className={styles.rank}>{index + 1}</span>
          <span className={styles.name}>{org.nombre}</span>
          <span className={styles.count}>{org.total_programas} programas</span>
        </li>
      ))}
    </ol>
  );
}
