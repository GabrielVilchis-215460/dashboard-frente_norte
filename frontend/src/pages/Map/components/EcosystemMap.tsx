// Mapa interactivo principal con Leaflet

import { useEffect, useRef, useCallback } from 'react';
import type { PinMapa } from '../../../types';
import { getTipoConfig } from './mapConfig';
import { JUAREZ_CENTER, DEFAULT_ZOOM } from './mapConfig';
import styles from './EcosystemMap.module.css';

interface Props {
  pins: PinMapa[];
  mode: 'pins' | 'heatmap';
  selectedId: number | null;
  onPinClick: (id: number) => void;
}

// Genera el SVG de un pin circular con el color del tipo
function pinSvg(color: string, animated: boolean, dimmed: boolean): string {
  const opacity = dimmed ? 0.35 : 1;
  const anim = animated && !dimmed
    ? `<animate attributeName="opacity" values="1;0.55;1" dur="2.4s" repeatCount="indefinite"/>`
    : '';
  return `
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
      <circle cx="8" cy="8" r="6" fill="${color}" opacity="${opacity}"
        stroke="rgba(255,255,255,0.5)" stroke-width="1.5">
        ${anim}
      </circle>
    </svg>
  `;
}

export function EcosystemMap({ pins, mode, selectedId, onPinClick }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<import('leaflet').Map | null>(null);
  const markersRef = useRef<Map<number, import('leaflet').Marker>>(new Map());
  const heatLayerRef = useRef<any>(null);
  const markerLayerRef = useRef<import('leaflet').LayerGroup | null>(null);

  // Inicializar el mapa
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    import('leaflet').then((L) => {
      const map = L.map(containerRef.current!, {
        center: JUAREZ_CENTER,
        zoom: DEFAULT_ZOOM,
        zoomControl: true,
        attributionControl: false,
      });

      L.tileLayer(
        'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        { maxZoom: 19 }
      ).addTo(map);

      markerLayerRef.current = L.layerGroup().addTo(map);
      mapRef.current = map;

      setTimeout(() => map.invalidateSize(), 100);
    });

    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
      markersRef.current.clear();
    };
  }, []);

  // Actualizar pines cuando cambian los datos o el modo
  useEffect(() => {
    if (!mapRef.current) return;

    import('leaflet').then((L) => {
      // Limpiar capa de marcadores
      markerLayerRef.current?.clearLayers();
      markersRef.current.clear();

      // Limpiar heatmap anterior
      if (heatLayerRef.current) {
        mapRef.current!.removeLayer(heatLayerRef.current);
        heatLayerRef.current = null;
      }

      const pinsConCoords = pins.filter((p) => p.latitud && p.longitud);

      if (mode === 'heatmap') {
        const heatData = pinsConCoords.map((p) => [
          p.latitud!,
          p.longitud!,
          Math.max(1, p.total_programas),
        ]);

        import('leaflet.heat').then(() => {
          if (!mapRef.current) return; // guarda: componente desmontado durante import
          const L_any = L as any;
          heatLayerRef.current = L_any.heatLayer(heatData, {
            radius: 30,
            blur: 20,
            maxZoom: 14,
            gradient: { 0.2: '#38bdf8', 0.5: '#2dd4bf', 0.8: '#34d399', 1.0: '#fbbf24' },
          }).addTo(mapRef.current);
        });
        return;
      }

      // Modo pines
      pinsConCoords.forEach((pin) => {
        const { color } = getTipoConfig(pin.tipo);
        const dimmed = selectedId !== null && selectedId !== pin.id;
        const animated = selectedId === null || selectedId === pin.id;

        const icon = L.divIcon({
          className: '',
          html: pinSvg(color, animated, dimmed),
          iconSize: [16, 16],
          iconAnchor: [8, 8],
        });

        const marker = L.marker([pin.latitud!, pin.longitud!], { icon });
        marker.on('click', () => onPinClick(pin.id));
        markerLayerRef.current!.addLayer(marker);
        markersRef.current.set(pin.id, marker);
      });
    });
  }, [pins, mode, selectedId, onPinClick]);

  // Centrar mapa cuando se selecciona un pin
  useEffect(() => {
    if (!mapRef.current || selectedId === null) return;
    const marker = markersRef.current.get(selectedId);
    if (!marker) return;

    const latlng = marker.getLatLng();
    mapRef.current.flyTo(
      [latlng.lat + 0.008, latlng.lng],
      13,
      { duration: 0.8, easeLinearity: 0.4 }
    );
  }, [selectedId]);

  return <div ref={containerRef} className={styles.map} />;
}
