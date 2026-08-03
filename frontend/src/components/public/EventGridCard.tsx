import { useState } from 'react';
import { Link } from 'react-router-dom';
import { IconCalendar, IconMapPin, IconCalendarEvent } from '@tabler/icons-react';
import { EventTag } from '../../pages/Events/components/EventTag';
import { formatFechaEvento, formatHorario } from '../../utils/format';
import { eventDetailPath } from '../../constants/routes';
import type { Evento } from '../../types';
import styles from './EventGridCard.module.css';

interface Props {
  evento: Evento;
}

export function EventGridCard({ evento }: Props) {
  const [imgError, setImgError] = useState(false);

  return (
    <Link to={eventDetailPath(evento.id)} className={styles.card}>
      <div className={styles.imgSlot}>
        {evento.imagen_url && !imgError ? (
          <img
            src={evento.imagen_url}
            alt={evento.nombre}
            className={styles.img}
            onError={() => setImgError(true)}
          />
        ) : (
          <div className={styles.imgPlaceholder}>
            <IconCalendarEvent size={32} className={styles.imgPlaceholderIcon} />
          </div>
        )}
      </div>

      <div className={styles.body}>
        <h3 className={styles.title}>{evento.nombre}</h3>
        {evento.organizacion && (
          <span className={styles.org}>{evento.organizacion.nombre}</span>
        )}

        <div className={styles.meta}>
          <span className={styles.metaRow}>
            <IconCalendar size={12} stroke={1.5} />
            {formatFechaEvento(evento.fecha, evento.fecha_fin)}
            {evento.hora_inicio && ` · ${formatHorario(evento.hora_inicio, evento.hora_fin)}`}
          </span>
          {evento.ubicacion && (
            <span className={styles.metaRow}>
              <IconMapPin size={12} stroke={1.5} />
              {evento.ubicacion}
            </span>
          )}
        </div>

        {(evento.tipo || evento.enfoque) && (
          <div className={styles.tags}>
            {evento.tipo && <EventTag label={evento.tipo} variant="tipo" />}
            {evento.enfoque && <EventTag label={evento.enfoque} variant="enfoque" />}
          </div>
        )}
      </div>
    </Link>
  );
}