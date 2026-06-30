import { useEffect, useRef } from 'react';
import { JUAREZ_CENTER } from '../Map/components/mapConfig';
import styles from './LocationPicker.module.css';

interface LocationPickerProps {
  latitud?: number;
  longitud?: number;
  onChange: (lat: number | undefined, lng: number | undefined) => void;
}

export function LocationPicker({ latitud, longitud, onChange }: LocationPickerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<import('leaflet').Map | null>(null);
  const markerRef = useRef<import('leaflet').Marker | null>(null);
  const LRef = useRef<typeof import('leaflet') | null>(null);

  // Coloca o mueve el pin — solo funciona si L y el mapa ya están listos
  function placeMarker(lat: number, lng: number) {
    const L = LRef.current;
    const map = mapRef.current;
    if (!L || !map) return;

    const pos: [number, number] = [lat, lng];
    if (markerRef.current) {
      markerRef.current.setLatLng(pos);
    } else {
      markerRef.current = L.marker(pos, { draggable: true }).addTo(map);
      markerRef.current.on('dragend', () => {
        const p = markerRef.current!.getLatLng();
        onChange(parseFloat(p.lat.toFixed(6)), parseFloat(p.lng.toFixed(6)));
      });
    }
  }

  // Inicializar mapa — guarda L en ref para que otros efectos lo usen
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    import('leaflet').then((L) => {
      LRef.current = L;

      const map = L.map(containerRef.current!, {
        center: (latitud && longitud) ? [latitud, longitud] : JUAREZ_CENTER,
        zoom: (latitud && longitud) ? 15 : 13,
        zoomControl: true,
        attributionControl: false,
      });

      L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        { maxZoom: 19, attribution: 'Tiles © Esri' }
      ).addTo(map);

      mapRef.current = map;

      // Colocar pin inicial si ya hay coordenadas
      if (latitud && longitud) placeMarker(latitud, longitud);

      // Click en el mapa → colocar/mover pin
      map.on('click', (e) => {
        const lat = parseFloat(e.latlng.lat.toFixed(6));
        const lng = parseFloat(e.latlng.lng.toFixed(6));
        placeMarker(lat, lng);
        onChange(lat, lng);
      });

      setTimeout(() => map.invalidateSize(), 150);
    });

    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
      markerRef.current = null;
      LRef.current = null;
    };
  }, []);

  // Sincronizar pin cuando cambian las coordenadas desde los inputs
  useEffect(() => {
    if (!mapRef.current || !LRef.current) return;

    if (latitud && longitud) {
      placeMarker(latitud, longitud);
      mapRef.current.setView([latitud, longitud], mapRef.current.getZoom());
    } else {
      if (markerRef.current) {
        markerRef.current.remove();
        markerRef.current = null;
      }
    }
  }, [latitud, longitud]);

  return (
    <div className={styles.wrapper}>
      <p className={styles.hint}>
        Haz clic en el mapa para colocar el pin, escribe las coordenadas manualmente o arrastra el pin para ajustar.
      </p>

      <div ref={containerRef} className={styles.mapContainer} />

      <div className={styles.coords}>
        <div className={styles.fieldGroup}>
          <label className={styles.label}>Latitud</label>
          <input
            className={styles.input}
            type="number"
            step="any"
            placeholder="31.7059"
            value={latitud ?? ''}
            onChange={(e) => onChange(e.target.value ? parseFloat(e.target.value) : undefined, longitud)}
          />
        </div>
        <div className={styles.fieldGroup}>
          <label className={styles.label}>Longitud</label>
          <input
            className={styles.input}
            type="number"
            step="any"
            placeholder="-106.4245"
            value={longitud ?? ''}
            onChange={(e) => onChange(latitud, e.target.value ? parseFloat(e.target.value) : undefined)}
          />
        </div>
      </div>

      {(latitud || longitud) && (
        <button className={styles.clearBtn} onClick={() => onChange(undefined, undefined)} type="button">
          Quitar ubicación
        </button>
      )}
    </div>
  );
}
