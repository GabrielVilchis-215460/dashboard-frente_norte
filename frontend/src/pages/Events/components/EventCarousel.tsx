// Carrusel de eventos proximos

import { useState } from 'react';
import {
  IconChevronLeft,
  IconChevronRight,
  IconCalendar,
  IconMapPin,
  IconExternalLink,
} from '@tabler/icons-react';
import { Skeleton } from '../../../components/ui';
import { EventTag } from './EventTag';
import { formatFechaEvento, formatHorario } from '../../../utils/format';
import type { Evento } from '../../../types';
import styles from './EventCarousel.module.css';

interface Props {
  eventos: Evento[];
  loading: boolean;
}

export function EventCarousel({ eventos, loading }: Props) {
  const [index, setIndex] = useState(0);
  const [imgFailed, setImgFailed] = useState(false);

  if (loading) {
    return (
      <div className={styles.skeleton}>
        <Skeleton width="100%" height="180px" borderRadius="12px" />
        <Skeleton width="70%" height="20px" />
        <Skeleton width="40%" height="14px" />
        <Skeleton width="100%" height="48px" />
      </div>
    );
  }

  if (!eventos.length) {
    return <p className={styles.empty}>No hay eventos próximos</p>;
  }

  const total = eventos.length;
  const ev = eventos[index];
  const hasImage = !!ev.imagen_url && !imgFailed;

  const prev = () => {
    setIndex((i) => (i - 1 + total) % total);
    setImgFailed(false);
  };
  const next = () => {
    setIndex((i) => (i + 1) % total);
    setImgFailed(false);
  };

  return (
    <div className={styles.carousel}>
      <div className={styles.counter}>{index + 1} / {total}</div>

      <div className={styles.body}>
        <button className={styles.navBtn} onClick={prev} disabled={total <= 1}>
          <IconChevronLeft size={18} stroke={1.5} />
        </button>

        <div className={`${styles.card} animate-fade-in`} key={ev.id}>
          {/* Imagen — se omite completamente si no hay o falla */}
          {hasImage && (
            <div className={styles.imgWrapper}>
              <img
                src={ev.imagen_url!}
                alt={ev.nombre}
                className={styles.img}
                onError={() => setImgFailed(true)}
              />
            </div>
          )}

          <div className={styles.content}>
            {/* Nombre + link externo */}
            <div className={styles.titleRow}>
              <h4 className={styles.title}>
                {ev.url_original ? (
                  <a
                    href={ev.url_original}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={styles.titleLink}
                  >
                    {ev.nombre}
                    <IconExternalLink size={13} stroke={1.5} className={styles.extIcon} />
                  </a>
                ) : (
                  ev.nombre
                )}
              </h4>
            </div>

            {/* Organización */}
            {ev.organizacion && (
              <span className={styles.org}>{ev.organizacion.nombre}</span>
            )}

            {/* Meta */}
            <div className={styles.meta}>
              <span className={styles.metaRow}>
                <IconCalendar size={12} stroke={1.5} />
                {formatFechaEvento(ev.fecha, ev.fecha_fin)}
                {ev.hora_inicio && ` · ${formatHorario(ev.hora_inicio, ev.hora_fin)}`}
              </span>
              {ev.ubicacion && (
                <span className={styles.metaRow}>
                  <IconMapPin size={12} stroke={1.5} />
                  {ev.ubicacion}
                </span>
              )}
            </div>

            {/* Descripción truncada */}
            {ev.descripcion && (
              <p className={styles.desc}>{ev.descripcion}</p>
            )}

            {/* Tags */}
            {(ev.tipo || ev.enfoque) && (
              <div className={styles.tags}>
                {ev.tipo && <EventTag label={ev.tipo} variant="tipo" />}
                {ev.enfoque && <EventTag label={ev.enfoque} variant="enfoque" />}
              </div>
            )}
          </div>
        </div>

        <button className={styles.navBtn} onClick={next} disabled={total <= 1}>
          <IconChevronRight size={18} stroke={1.5} />
        </button>
      </div>
    </div>
  );
}