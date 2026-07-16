import { useState, useEffect, useRef, useCallback } from 'react';
import {
  IconCalendar,
  IconClock,
  IconMapPin,
  IconBuilding,
  IconTarget,
  IconTag,
  IconExternalLink,
} from '@tabler/icons-react';
import { PageHeader } from '../../components/layout';
import { Skeleton } from '../../components/ui';
import { useApi } from '../../hooks/useApi';
import { api } from '../../services/api';
import type { Evento, EventoMapPoint } from '../../types';
import { formatFechaEvento, formatHorario } from '../../utils/format';
import styles from './Events.module.css';

type Tab = 'proximos' | 'historial';

const JUAREZ_CENTER: [number, number] = [31.715, -106.4245];
const DEFAULT_ZOOM = 12;

// ── Mapa de eventos ───────────────────────────────────────────────────────────

function EventsMap({
  puntos,
  selectedOrgId,
  onPinClick,
}: {
  puntos: EventoMapPoint[];
  selectedOrgId: number | null;
  onPinClick: (orgId: number) => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<import('leaflet').Map | null>(null);
  const [mapReady, setMapReady] = useState(false);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    import('leaflet').then((L) => {
      const map = L.map(containerRef.current!, {
        center: JUAREZ_CENTER,
        zoom: DEFAULT_ZOOM,
        zoomControl: true,
        attributionControl: false,
      });
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
      }).addTo(map);
      mapRef.current = map;
      setTimeout(() => { map.invalidateSize(); setMapReady(true); }, 100);
    });
    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
      setMapReady(false);
    };
  }, []);

  useEffect(() => {
    if (!mapReady || !mapRef.current) return;
    import('leaflet').then((L) => {
      mapRef.current!.eachLayer((layer) => {
        if (layer instanceof L.Marker) layer.remove();
      });
      puntos.forEach((punto) => {
        const isSelected = selectedOrgId === punto.organizacion_id;
        const color = isSelected ? '#38bdf8' : '#2dd4bf';
        const size = isSelected ? 18 : 14;
        const icon = L.divIcon({
          className: '',
          html: `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 16 16">
            <circle cx="8" cy="8" r="6" fill="${color}" stroke="rgba(255,255,255,0.6)" stroke-width="1.5">
              ${isSelected ? '<animate attributeName="opacity" values="1;0.5;1" dur="1.5s" repeatCount="indefinite"/>' : ''}
            </circle>
            <text x="8" y="11" text-anchor="middle" font-size="7" fill="#0c2340" font-weight="bold">${punto.total_eventos}</text>
          </svg>`,
          iconSize: [size, size],
          iconAnchor: [size / 2, size / 2],
        });
        const marker = L.marker([punto.latitud, punto.longitud], { icon });
        marker.bindTooltip(`<strong>${punto.organizacion_nombre}</strong><br/>${punto.total_eventos} evento${punto.total_eventos !== 1 ? 's' : ''}`, {
          direction: 'top',
          className: '',
        });
        marker.on('click', () => onPinClick(punto.organizacion_id));
        marker.addTo(mapRef.current!);
      });
    });
  }, [mapReady, puntos, selectedOrgId, onPinClick]);

  return <div ref={containerRef} className={styles.mapContainer} />;
}

// ── Tarjeta de evento ─────────────────────────────────────────────────────────

function EventCard({
  evento,
  selected,
  onClick,
}: {
  evento: Evento;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <div
      className={`${styles.eventCard} ${selected ? styles.selected : ''} animate-fade-in-up`}
      onClick={onClick}
    >
      <div className={styles.eventCardImg}>
        {evento.imagen_url ? (
          <img src={evento.imagen_url} alt={evento.nombre} />
        ) : (
          '📅'
        )}
      </div>
      <div className={styles.eventCardBody}>
        <p className={styles.eventCardTitle}>{evento.nombre}</p>
        <div className={styles.eventCardMeta}>
          <span><IconCalendar size={12} stroke={1.5} /> {formatFechaEvento(evento.fecha, evento.fecha_fin)}</span>
          {evento.hora_inicio && (
            <span><IconClock size={12} stroke={1.5} /> {formatHorario(evento.hora_inicio, evento.hora_fin)}</span>
          )}
          {evento.ubicacion && <span><IconMapPin size={12} stroke={1.5} /> {evento.ubicacion}</span>}
        </div>
        {evento.organizacion && (
          <p className={styles.eventCardOrg}>{evento.organizacion.nombre}</p>
        )}
        {evento.tipo && <span className={styles.pill}>{evento.tipo}</span>}
      </div>
    </div>
  );
}

// ── Modal de detalle ──────────────────────────────────────────────────────────

function EventModal({ evento, onClose }: { evento: Evento; onClose: () => void }) {
  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div
          className={styles.modalImg}
          style={evento.imagen_url ? { backgroundImage: `url(${evento.imagen_url})` } : undefined}
        >
          {evento.imagen_url && <div className={styles.modalImgBlur} />}
          {evento.imagen_url ? <img src={evento.imagen_url} alt={evento.nombre} /> : '📅'}
        </div>
        <div className={styles.modalBody}>
          <h2 className={styles.modalTitle}>{evento.nombre}</h2>
          <div className={styles.modalMeta}>
            <span><IconCalendar size={15} stroke={1.5} /> {formatFechaEvento(evento.fecha, evento.fecha_fin)}</span>
            {evento.hora_inicio && (
              <span><IconClock size={15} stroke={1.5} /> {formatHorario(evento.hora_inicio, evento.hora_fin)}</span>
            )}
            {evento.ubicacion && <span><IconMapPin size={15} stroke={1.5} /> {evento.ubicacion}</span>}
            {evento.organizacion && <span><IconBuilding size={15} stroke={1.5} /> {evento.organizacion.nombre}</span>}
            {evento.enfoque && <span><IconTarget size={15} stroke={1.5} /> {evento.enfoque}</span>}
            {evento.tipo && <span><IconTag size={15} stroke={1.5} /> {evento.tipo}</span>}
          </div>
          {evento.descripcion && (
            <p className={styles.modalDesc}>{evento.descripcion}</p>
          )}
          <div className={styles.modalActions}>
            {evento.url_original && (
              <a
                href={evento.url_original}
                target="_blank"
                rel="noopener noreferrer"
                className={styles.linkBtn}
              >
                <IconExternalLink size={15} stroke={2} style={{ marginRight: 6 }} />
                Ver publicación
              </a>
            )}
            <button className={styles.closeBtn} onClick={onClose}>
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Página principal ──────────────────────────────────────────────────────────

export function Events() {
  const [tab, setTab] = useState<Tab>('proximos');
  const [selectedEvento, setSelectedEvento] = useState<Evento | null>(null);
  const [selectedOrgId, setSelectedOrgId] = useState<number | null>(null);
  const [filtroTipo, setFiltroTipo] = useState('');
  const [filtroEnfoque, setFiltroEnfoque] = useState('');

  const { data: proximos, loading: loadingP } = useApi(() => api.getEventosProximos(), []);
  const { data: historial, loading: loadingH } = useApi(
    () => api.getEventosHistorial({ limit: 100 }),
    []
  );
  const { data: mapaData, loading: loadingM } = useApi(() => api.getEventosMapa(), []);

  const eventos = tab === 'proximos' ? (proximos ?? []) : (historial ?? []);
  const loading = tab === 'proximos' ? loadingP : loadingH;

  const tiposUnicos = [...new Set(eventos.flatMap((e) => e.tipo ? [e.tipo] : []))];
  const enfoquesUnicos = [...new Set(eventos.flatMap((e) => e.enfoque ? [e.enfoque] : []))];

  const eventosFiltrados = eventos.filter((e) => {
    if (filtroTipo && e.tipo !== filtroTipo) return false;
    if (filtroEnfoque && e.enfoque !== filtroEnfoque) return false;
    if (selectedOrgId && e.organizacion?.id !== selectedOrgId) return false;
    return true;
  });

  const handlePinClick = useCallback((orgId: number) => {
    setSelectedOrgId((prev) => (prev === orgId ? null : orgId));
    setTab('proximos');
  }, []);

  return (
    <div className={styles.page}>
      <PageHeader
        title="Eventos"
        description="Actividades y eventos del ecosistema STEM de Ciudad Juárez"
      />

      <div className={styles.mainLayout}>
        {/* Mapa */}
        <div className={styles.mapPanel}>
          {loadingM ? (
            <Skeleton width="100%" height="100%" />
          ) : (
            <EventsMap
              puntos={mapaData ?? []}
              selectedOrgId={selectedOrgId}
              onPinClick={handlePinClick}
            />
          )}
        </div>

        {/* Lista */}
        <div className={styles.listPanel}>
          <div className={styles.tabs}>
            <button
              className={`${styles.tab} ${tab === 'proximos' ? styles.tabActive : ''}`}
              onClick={() => { setTab('proximos'); setSelectedOrgId(null); }}
            >
              Próximos eventos
            </button>
            <button
              className={`${styles.tab} ${tab === 'historial' ? styles.tabActive : ''}`}
              onClick={() => { setTab('historial'); setSelectedOrgId(null); }}
            >
              Historial
            </button>
          </div>

          <div className={styles.filtersRow}>
            <select
              className={styles.filterSelect}
              value={filtroTipo}
              onChange={(e) => setFiltroTipo(e.target.value)}
            >
              <option value="">Todos los tipos</option>
              {tiposUnicos.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
            <select
              className={styles.filterSelect}
              value={filtroEnfoque}
              onChange={(e) => setFiltroEnfoque(e.target.value)}
            >
              <option value="">Todos los enfoques</option>
              {enfoquesUnicos.map((e) => <option key={e} value={e}>{e}</option>)}
            </select>
            {selectedOrgId && (
              <button className={styles.closeBtn} onClick={() => setSelectedOrgId(null)}>
                ✕ Limpiar filtro mapa
              </button>
            )}
          </div>

          <div className={styles.eventsList}>
            {loading ? (
              <div className={styles.loadingRow}>
                {Array.from({ length: 4 }).map((_, i) => (
                  <Skeleton key={i} height="80px" borderRadius="8px" />
                ))}
              </div>
            ) : eventosFiltrados.length === 0 ? (
              <p className={styles.empty}>
                {tab === 'proximos' ? 'No hay eventos próximos.' : 'No hay eventos en el historial.'}
              </p>
            ) : (
              eventosFiltrados.map((ev) => (
                <EventCard
                  key={ev.id}
                  evento={ev}
                  selected={selectedEvento?.id === ev.id}
                  onClick={() => setSelectedEvento(ev)}
                />
              ))
            )}
          </div>
        </div>
      </div>

      {selectedEvento && (
        <EventModal evento={selectedEvento} onClose={() => setSelectedEvento(null)} />
      )}
    </div>
  );
}
