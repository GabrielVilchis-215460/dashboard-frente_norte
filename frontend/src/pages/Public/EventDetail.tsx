import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { IconArrowLeft, IconExternalLink } from '@tabler/icons-react';
import { EventTag } from '../../pages/Events/components/EventTag';
import { PublicMap } from '../../components/public/PublicMap';
import { Skeleton } from '../../components/ui';
import { publicApi } from '../../services/publicApi';
import { formatFechaEvento, formatHorario } from '../../utils/format';
import { ROUTES } from '../../constants/routes';
import type { Evento, EventoMapPoint } from '../../types';
import styles from './EventDetail.module.css';

export function EventDetail() {
  const { id } = useParams<{ id: string }>();
  const [evento, setEvento] = useState<Evento | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    setNotFound(false);
    publicApi
      .getEventoDetalle(id)
      .then(setEvento)
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className={styles.page}>
        <Skeleton width="30%" height="20px" />
        <Skeleton width="60%" height="40px" style={{ marginTop: 16 }} />
        <Skeleton width="100%" height="360px" borderRadius="16px" style={{ marginTop: 24 }} />
      </div>
    );
  }

  if (notFound || !evento) {
    return (
      <div className={styles.page}>
        <p className={styles.notFound}>No encontramos este evento.</p>
        <Link to={ROUTES.EVENTS} className={styles.backLink}>
          <IconArrowLeft size={16} stroke={1.8} /> Volver
        </Link>
      </div>
    );
  }

  const mapaPoint: EventoMapPoint | null =
    evento.organizacion?.latitud && evento.organizacion?.longitud
      ? {
          organizacion_id: evento.organizacion.id,
          organizacion_nombre: evento.organizacion.nombre,
          latitud: evento.organizacion.latitud,
          longitud: evento.organizacion.longitud,
          total_eventos: 1,
          eventos: [evento],
        }
      : null;

  return (
    <div className={styles.page}>
      <Link to={ROUTES.EVENTS} className={styles.backLink}>
        <IconArrowLeft size={18} stroke={1.8} /> Volver
      </Link>

      <div className={styles.headerRow}>
        <div>
          <h1 className={styles.title}>{evento.nombre}</h1>
          <div className={styles.subRow}>
            {evento.organizacion && <span className={styles.org}>{evento.organizacion.nombre}</span>}
            {evento.tipo && <EventTag label={evento.tipo} variant="tipo" />}
            {evento.enfoque && <EventTag label={evento.enfoque} variant="enfoque" />}
          </div>
        </div>

        {evento.url_original && (
          <a
            href={evento.url_original}
            target="_blank"
            rel="noopener noreferrer"
            className={styles.verPublicacion}
          >
            Ver publicación <IconExternalLink size={16} stroke={1.8} />
          </a>
        )}
      </div>

      {evento.imagen_url && (
        <div
          className={styles.heroImgWrap}
          style={{ backgroundImage: `url("${evento.imagen_url.replace(/"/g, '%22')}")` }}
        >
          <img src={evento.imagen_url} alt={evento.nombre} className={styles.heroImg} />
        </div>
      )}

      <div className={styles.contentGrid}>
        <div>
          <h2 className={styles.sectionTitle}>Sobre el evento</h2>
          <p className={styles.description}>
            {evento.descripcion || 'Este evento no tiene una descripción disponible.'}
          </p>
        </div>

        <aside className={styles.infoPanel}>
          <div className={styles.infoBlock}>
            <span className={styles.infoLabel}>Fecha</span>
            <span className={styles.infoValue}>
              {formatFechaEvento(evento.fecha, evento.fecha_fin)}
            </span>
          </div>

          {evento.hora_inicio && (
            <div className={styles.infoBlock}>
              <span className={styles.infoLabel}>Horario</span>
              <span className={styles.infoValue}>
                {formatHorario(evento.hora_inicio, evento.hora_fin)}
              </span>
            </div>
          )}

          {evento.ubicacion && (
            <div className={styles.infoBlock}>
              <span className={styles.infoLabel}>Ubicación</span>
              <span className={styles.infoValue}>{evento.ubicacion}</span>
            </div>
          )}
        </aside>
      </div>

      {mapaPoint && (
        <section className={styles.mapSection}>
          <h2 className={styles.sectionTitle}>Mapa</h2>
          <PublicMap
            eventPoints={[mapaPoint]}
            height={360}
            center={[mapaPoint.latitud, mapaPoint.longitud]}
            zoom={15}
            showEventCount={false}
          />
        </section>
      )}
    </div>
  );
}