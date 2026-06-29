// Carrusel de programas destacados

import { useState } from 'react';
import { IconChevronLeft, IconChevronRight } from '@tabler/icons-react';
import type { ProgramaDetalle } from '../../../types';
import { Skeleton } from '../../../components/ui';
import styles from './ProgramCarousel.module.css';

interface Props {
  programas: ProgramaDetalle[];
  loading: boolean;
}

function rangeLabel(pct: number): string {
  if (pct >= 76) return '75% a 100% de participación femenina';
  if (pct >= 51) return '51% a 75% de participación femenina';
  if (pct >= 26) return '26% a 50% de participación femenina';
  return '0% a 25% de participación femenina';
}

export function ProgramCarousel({ programas, loading }: Props) {
  const [index, setIndex] = useState(0);

  if (loading) {
    return (
      <div className={styles.cardInner}>
        <Skeleton width="50%" height="22px" />
        <Skeleton width="30%" height="14px" />
        <Skeleton width="100%" height="120px" borderRadius="12px" />
      </div>
    );
  }

  if (!programas.length) {
    return <p className={styles.empty}>No hay programas destacados disponibles</p>;
  }

  const total = programas.length;
  const current = programas[index];

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
          aria-label="Programa anterior"
          disabled={total <= 1}
        >
          <IconChevronLeft size={20} stroke={1.5} />
        </button>

        <div className={`${styles.content} animate-fade-in`} key={index}>
          <h4 className={styles.name}>{current.nombre}</h4>
          <span className={styles.org}>{current.organizacion}</span>
          <span className={styles.range}>{rangeLabel(current.pct_mujeres)}</span>
          <p className={styles.desc}>
            {current.descripcion ?? 'Sin descripción disponible'}
          </p>
        </div>

        <button
          className={styles.navBtn}
          onClick={next}
          aria-label="Programa siguiente"
          disabled={total <= 1}
        >
          <IconChevronRight size={20} stroke={1.5} />
        </button>
      </div>
    </div>
  );
}