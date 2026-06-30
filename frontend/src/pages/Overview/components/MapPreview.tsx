// MapPreview: Mini mapa en Panorama General
// Leaflet con mapa oscuro + pines de organizaciones

import { useEffect, useRef } from 'react';
import type { PreviewMapaPoint } from '../../../types';
import { Skeleton } from '../../../components/ui';
import styles from './MapPreview.module.css';

// Coordenadas de Ciudad Juárez
const JUAREZ_CENTER: [number, number] = [31.7150, -106.4245];
const DEFAULT_ZOOM = 13;

interface Props {
  points: PreviewMapaPoint[];
  loading: boolean;
  className?: string;
}

export function MapPreview({ points, loading, className = '' }: Props) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<import('leaflet').Map | null>(null);

  useEffect(() => {
    if (loading || !mapRef.current || mapInstanceRef.current) return;

    // Import dinámico de Leaflet para evitar SSR issues
    import('leaflet').then((L) => {
      // Tile oscuro tipo CartoDB Dark Matter (sin API key)
      const map = L.map(mapRef.current!, {
        center: JUAREZ_CENTER,
        zoom: DEFAULT_ZOOM,
        zoomControl: false,
        attributionControl: false,
        dragging: false,
        scrollWheelZoom: false,
      });

      L.tileLayer(
        'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        { maxZoom: 19 }
      ).addTo(map);

      mapInstanceRef.current = map;

      // Leaflet necesita recalcular tras montarse en un contenedor flexible
      setTimeout(() => map.invalidateSize(), 100);
    });

    return () => {
      mapInstanceRef.current?.remove();
      mapInstanceRef.current = null;
    };
  }, [loading]);

  useEffect(() => {
    if (!mapInstanceRef.current || points.length === 0) return;

    import('leaflet').then((L) => {
      points.forEach((point) => {
        const icon = L.divIcon({
          className: '',
          html: `<div class="${styles.pin}" title="${point.nombre}"></div>`,
          iconSize: [12, 12],
          iconAnchor: [6, 6],
        });

        L.marker([point.latitud, point.longitud], { icon })
          .addTo(mapInstanceRef.current!)
          .bindTooltip(
            `<strong>${point.nombre}</strong><br/>${point.total_programas} programas`,
            { className: styles.leafletTooltip, direction: 'top' }
          );
      });
    });
  }, [points]);

  if (loading) {
    return (
      <div className={`${styles.wrapper} ${className}`}>
        <Skeleton width="100%" height="100%" borderRadius="16px" />
      </div>
    );
  }

  return (
    <div className={`${styles.wrapper} ${className}`}>
      {/* Título integrado sobre el mapa */}
      <div className={styles.title}>Mapa del Ecosistema</div>
      {/* El mapa ocupa todo el contenedor */}
      <div ref={mapRef} className={styles.map} />
    </div>
  );
}