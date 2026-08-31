// Mapa interactivo principal con Leaflet

import { useEffect, useRef } from 'react';
import type { PinMapa, EventoMapPoint } from '../../../types';
import { getTipoConfig } from './mapConfig';
import { JUAREZ_CENTER, DEFAULT_ZOOM } from './mapConfig';
import styles from './EcosystemMap.module.css';
import L from 'leaflet';
import 'leaflet.heat';

export type MapMode = 'pins' | 'heatmap' | 'events';

interface Props {
  pins: PinMapa[];
  eventPoints?: EventoMapPoint[];
  mode: MapMode;
  selectedId: number | null;
  onPinClick: (id: number, lat: number, lng: number) => void;
  center?: [number, number];
  zoom?: number;
  showEventCount?: boolean;
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
    </svg>`;
}

function eventPinSvg(count: number, showCount: boolean): string {
  if (!showCount) {
    return `
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 22 22">
        <circle cx="11" cy="11" r="9" fill="#38bdf8"
          stroke="rgba(255,255,255,0.5)" stroke-width="1.5">
          <animate attributeName="opacity" values="1;0.55;1" dur="2.4s" repeatCount="indefinite"/>
        </circle>
      </svg>`;
  }
  return `
    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 22 22">
      <circle cx="11" cy="11" r="9" fill="#38bdf8"
        stroke="rgba(255,255,255,0.5)" stroke-width="1.5">
        <animate attributeName="opacity" values="1;0.55;1" dur="2.4s" repeatCount="indefinite"/>
      </circle>
      <text x="11" y="15" text-anchor="middle"
        font-size="9" font-weight="700" fill="#0c2340">${count}</text>
    </svg>`;
}

export function EcosystemMap({
  pins,
  eventPoints = [],
  mode,
  selectedId,
  onPinClick,
  center,
  zoom,
  showEventCount = true,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const markersRef = useRef<Map<number, L.Marker>>(new Map());
  const heatLayerRef = useRef<any>(null);
  const markerLayerRef = useRef<L.LayerGroup | null>(null);

  // Inicializar el mapa
  useEffect(() => {
    if (!containerRef.current) return;
    if ((containerRef.current as any)._leaflet_id) return;

    const isTouch = navigator.maxTouchPoints > 0;
    const container = containerRef.current;

    const map = L.map(container, {
      center: center ?? JUAREZ_CENTER,
      zoom: zoom ?? DEFAULT_ZOOM,
      zoomControl: !isTouch,
      attributionControl: true,
      doubleClickZoom: false,
      dragging: !isTouch,
      tap: false,
      scrollWheelZoom: false,
      touchZoom: isTouch,
      pinchZoom: isTouch,
    } as any);

    // ── Hint flotante ──────────────────────────────────────────────────────────
    const hint = document.createElement('div');
    hint.className = styles.mapHint;
    container.appendChild(hint);

    let hintTimer: ReturnType<typeof setTimeout>;

    function showHint(msg: string) {
      hint.textContent = msg;
      hint.classList.add(styles.mapHintVisible);
      clearTimeout(hintTimer);
      hintTimer = setTimeout(() => hint.classList.remove(styles.mapHintVisible), 2000);
    }

    if (isTouch) {
      // Móvil/tablet: un dedo → hint, dos dedos → zoom+pan
      let touchCount = 0;
      container.addEventListener('touchstart', (e) => {
        touchCount = e.touches.length;
        if (touchCount === 1) {
          showHint('Usa dos dedos para mover el mapa');
        }
        if (touchCount >= 2) {
          map.dragging.enable();
        }
      }, { passive: true });
      container.addEventListener('touchend', () => {
        touchCount = 0;
        map.dragging.disable();
      }, { passive: true });
    } else {
      // Desktop: drag libre, Alt+scroll para zoom
      map.dragging.enable();
      map.scrollWheelZoom.disable();

      container.addEventListener('wheel', (e: WheelEvent) => {
        if (e.altKey) {
          e.preventDefault();
          map.setZoom(map.getZoom() + (e.deltaY < 0 ? 1 : -1));
        } else {
          showHint('Mantén Alt + scroll para hacer zoom');
        }
      }, { passive: false });
    }

    L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      { maxZoom: 19, attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' }
    ).addTo(map);

    markerLayerRef.current = L.layerGroup().addTo(map);
    mapRef.current = map;

    setTimeout(() => map.invalidateSize(), 100);

    return () => {
      clearTimeout(hintTimer);
      map.remove();
      mapRef.current = null;
      markerLayerRef.current = null;
      markersRef.current.clear();
    };
  }, []);

  // Actualizar pines cuando cambian los datos o el modo
  useEffect(() => {
    if (!mapRef.current) return;
    const map = mapRef.current;

    // Limpiar capa de marcadores
    markerLayerRef.current?.clearLayers();
    markersRef.current.clear();

    // Limpiar heatmap anterior de manera síncrona y segura
    if (heatLayerRef.current) {
      map.removeLayer(heatLayerRef.current);
      heatLayerRef.current = null;
    }

    // ── Modo heatmap ──
    if (mode === 'heatmap') {
      const pinsConCoords = pins.filter((p) => p.latitud && p.longitud);
      const heatData = pinsConCoords.map((p) => [
        p.latitud!, p.longitud!, Math.max(1, p.total_programas),
      ]);

      const L_any = L as any;
      if (typeof L_any.heatLayer === 'function') {
        heatLayerRef.current = L_any.heatLayer(heatData, {
          radius: 30,
          blur: 20,
          maxZoom: 14,
          gradient: { 0.2: '#38bdf8', 0.5: '#2dd4bf', 0.8: '#34d399', 1.0: '#fbbf24' },
        }).addTo(map);
      }
      return;
    }

    // ── Modo eventos ──
    if (mode === 'events') {
      eventPoints.forEach((punto) => {
        const icon = L.divIcon({
          className: '',
          html: eventPinSvg(punto.total_eventos, showEventCount),
          iconSize: [22, 22],
          iconAnchor: [11, 11],
        });
        const preview = punto.eventos.slice(0, 3)
          .map((ev) => `<li>${ev.nombre}</li>`).join('');
        const mas = punto.total_eventos > 3
          ? `<li style="opacity:0.6">+${punto.total_eventos - 3} más</li>` : '';
        L.marker([punto.latitud, punto.longitud], { icon })
          .bindTooltip(
            `<strong>${punto.organizacion_nombre}</strong>
             <ul style="margin:4px 0 0;padding-left:14px;font-size:11px">${preview}${mas}</ul>`,
            { direction: 'top' }
          )
          .addTo(markerLayerRef.current!);
      });
      return;
    }

    // ── Modo pines ──
    pins.filter((p) => p.latitud && p.longitud).forEach((pin) => {
      // Tomamos el primer tipo del arreglo para asignarle color de manera segura
      const primerTipo = Array.isArray(pin.tipo) && pin.tipo.length > 0 ? pin.tipo[0] : (pin.tipo as unknown as string);
      const { color } = getTipoConfig(primerTipo);
      const dimmed = selectedId !== null && selectedId !== pin.id;
      const animated = selectedId === null || selectedId === pin.id;

      const icon = L.divIcon({
        className: '',
        html: pinSvg(color, animated, dimmed),
        iconSize: [16, 16],
        iconAnchor: [8, 8],
      });

      const marker = L.marker([pin.latitud!, pin.longitud!], { icon });
      marker.on('click', () => onPinClick(pin.id, pin.latitud!, pin.longitud!));
      markerLayerRef.current!.addLayer(marker);
      markersRef.current.set(pin.id, marker);
    });
  }, [pins, eventPoints, mode, selectedId, onPinClick, showEventCount]);

  // Centrar mapa cuando se selecciona un pin
  useEffect(() => {
    if (!mapRef.current || selectedId === null) return;
    const marker = markersRef.current.get(selectedId);
    if (!marker) return;

    const map = mapRef.current;
    const latlng = marker.getLatLng();
    const currentZoom = map.getZoom();
    const targetZoom = Math.max(currentZoom, 13); 

    // offset en píxeles reales (constante en pantalla, no en grados)
    const offsetPoint = map.project(latlng, targetZoom).subtract([0, 80]);
    const offsetLatLng = map.unproject(offsetPoint, targetZoom);

    map.flyTo(offsetLatLng, targetZoom, { duration: 0.8, easeLinearity: 0.4 });
  }, [selectedId]);

  return <div ref={containerRef} className={styles.map} />;
}