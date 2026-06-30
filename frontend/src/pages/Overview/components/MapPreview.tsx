// MapPreview: Mini mapa en Panorama General
// Leaflet con mapa oscuro + pines de organizaciones

import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { PreviewMapaPoint } from '../../../types';
import { Skeleton } from '../../../components/ui';
import { ROUTES } from '../../../constants/routes';
import styles from './MapPreview.module.css';

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
  const navigate = useNavigate();
  const [mapReady, setMapReady] = useState(false);

  useEffect(() => {
    if (loading || !mapRef.current || mapInstanceRef.current) return;

    import('leaflet').then((L) => {
      const map = L.map(mapRef.current!, {
        center: JUAREZ_CENTER,
        zoom: DEFAULT_ZOOM,
        zoomControl: false,
        attributionControl: false,
        dragging: false,
        scrollWheelZoom: false,
        doubleClickZoom: false,
      });

      L.tileLayer(
        'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        { maxZoom: 19 }
      ).addTo(map);

      mapInstanceRef.current = map;
      setTimeout(() => { map.invalidateSize(); setMapReady(true); }, 100);
    });

    return () => {
      mapInstanceRef.current?.remove();
      mapInstanceRef.current = null;
      setMapReady(false);
    };
  }, [loading]);

  useEffect(() => {
    if (!mapReady || !mapInstanceRef.current || points.length === 0) return;

    import('leaflet').then((L) => {
      // Limpiar marcadores anteriores para evitar duplicados en re-renders
      mapInstanceRef.current!.eachLayer((layer) => {
        if (layer instanceof L.Marker) layer.remove();
      });

      points.forEach((point) => {
        const icon = L.divIcon({
          className: '',
          html: `<div class="${styles.pin}" title="${point.nombre}"></div>`,
          iconSize: [12, 12],
          iconAnchor: [6, 6],
        });

        // Tooltip con logo, nombre y número de programas
        const logoHtml = point.logo_url
          ? `<img src="${point.logo_url}" alt="${point.nombre}" class="${styles.tooltipLogo}" onerror="this.style.display='none'" />`
          : '';

        const tooltipContent = `
          <div class="${styles.tooltipContent}">
            ${logoHtml}
            <div class="${styles.tooltipText}">
              <strong>${point.nombre}</strong>
              <span>${point.total_programas} programa${point.total_programas !== 1 ? 's' : ''}</span>
            </div>
          </div>
        `;

        const marker = L.marker([point.latitud, point.longitud], { icon })
          .addTo(mapInstanceRef.current!)
          .bindTooltip(tooltipContent, {
            className: styles.leafletTooltip,
            direction: 'top',
          });

        // Click en pin → navegar al mapa con el pin seleccionado
        marker.on('click', () => {
          navigate(`${ROUTES.MAP}?org=${point.id}`);
        });
      });
    });
  }, [points, navigate, mapReady]);

  if (loading) {
    return (
      <div className={`${styles.wrapper} ${className}`}>
        <Skeleton width="100%" height="100%" borderRadius="16px" />
      </div>
    );
  }

  return (
    <div className={`${styles.wrapper} ${className}`}>
      <div className={styles.title}>Mapa del Ecosistema</div>
      <div className={styles.hint}>Clic en un pin para ver el detalle</div>
      <div ref={mapRef} className={styles.map} />
    </div>
  );
}
