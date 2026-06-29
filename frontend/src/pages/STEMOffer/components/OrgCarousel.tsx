// Carrusel de organizaciones por especialidad

import { useState } from 'react';
import {
  IconChevronLeft,
  IconChevronRight,
  IconUsersGroup,
  IconSchool,
  IconBuilding,
} from '@tabler/icons-react';
import type { OrganizacionProgramas } from '../../../types';
import { Skeleton } from '../../../components/ui';
import { formatLabel } from '../../../utils/format';
import styles from './OrgCarousel.module.css';

interface Props {
  orgs: OrganizacionProgramas[];
  loading: boolean;
}

export function OrgCarousel({ orgs, loading }: Props) {
  const [index, setIndex] = useState(0);

  if (loading) {
    return (
      <div className={styles.cardInner}>
        <Skeleton width="120px" height="48px" borderRadius="8px" />
        <Skeleton width="60%" height="20px" />
        <Skeleton width="100%" height="80px" borderRadius="12px" />
      </div>
    );
  }

  if (!orgs.length) {
    return <p className={styles.empty}>No hay organizaciones disponibles</p>;
  }

  const total = orgs.length;
  const current = orgs[index];

  const prev = () => setIndex((i) => (i - 1 + total) % total);
  const next = () => setIndex((i) => (i + 1) % total);

  return (
    <div className={styles.carousel}>
      <div className={styles.counter}>
        {index + 1} / {total}
      </div>

      <div className={styles.body}>
        <button
          className={styles.navBtn}
          onClick={prev}
          aria-label="Organización anterior"
          disabled={total <= 1}
        >
          <IconChevronLeft size={20} stroke={1.5} />
        </button>

        <div className={`${styles.content} animate-fade-in`} key={index}>
          {/* Logo o placeholder */}
          {current.logo_url ? (
            <img
              src={current.logo_url}
              alt={current.organizacion}
              className={styles.logo}
            />
          ) : (
            <div className={styles.logoPlaceholder}>
              <IconBuilding size={28} stroke={1.5} />
            </div>
          )}
          {/* Nombre de la organización */}
          <h3 className={styles.orgName}>{current.organizacion}</h3>
          
          {/* Badges */}
          <div className={styles.badges}>
            {current.tipo_organizacion && current.tipo_organizacion !== 'No especificado' && (
              <span className={`${styles.badge} ${styles.badgeBlue}`}>
                <IconUsersGroup size={14} stroke={1.5} />
                {formatLabel(current.tipo_organizacion)}
              </span>
            )}
            {current.enfoque_principal && current.enfoque_principal !== 'No especificado' && (
              <span className={`${styles.badge} ${styles.badgeGreen}`}>
                <IconSchool size={14} stroke={1.5} />
                {formatLabel(current.enfoque_principal)}
              </span>
            )}
          </div>

          {/* Lista de programas */}
          <div className={styles.programsSection}>
            <span className={styles.programsLabel}>Programas ofertados:</span>
            <ul className={styles.programsList}>
              {current.programas.slice(0, 5).map((prog, i) => (
                <li key={i} className={styles.programItem}>{prog}</li>
              ))}
              {current.programas.length > 5 && (
                <li className={styles.programMore}>
                  +{current.programas.length - 5} más
                </li>
              )}
            </ul>
          </div>
        </div>

        <button
          className={styles.navBtn}
          onClick={next}
          aria-label="Organización siguiente"
          disabled={total <= 1}
        >
          <IconChevronRight size={20} stroke={1.5} />
        </button>
      </div>
    </div>
  );
}