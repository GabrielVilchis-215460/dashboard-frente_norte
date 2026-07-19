// Mapa del Ecosistema

import { useState, useCallback, useEffect } from 'react';
import {
  IconBuildingCommunity,
  IconFlame,
  IconCalendarEvent,
  IconChevronDown,
  IconChevronUp,
} from '@tabler/icons-react';
import { PageHeader } from '../../components/layout';
import { api } from '../../services/api';
import type { MapFilters, FichaActor, EventoMapPoint } from '../../types';
import { EcosystemMap, type MapMode } from './components/EcosystemMap';
import { FilterPanel } from './components/FilterPanel';
import { ActorSheet } from './components/ActorSheet';
import { TIPO_LEGEND } from './components/mapConfig';
import styles from './Map.module.css';

const EMPTY_FILTERS: MapFilters = { solo_con_coordenadas: true };

export function MapPage() {
  const [filters, setFilters] = useState<MapFilters>(EMPTY_FILTERS);
  const [mode, setMode] = useState<MapMode>('pins');
  const [filterOpen, setFilterOpen] = useState(false);
  const [modeMenuOpen, setModeMenuOpen] = useState(false);

  const [pins, setPins] = useState<any[]>([]);
  const [pinsLoading, setPinsLoading] = useState(true);

  const [eventPoints, setEventPoints] = useState<EventoMapPoint[]>([]);
  const [eventsLoading, setEventsLoading] = useState(false);

  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [ficha, setFicha] = useState<FichaActor | null>(null);
  const [fichaLoading, setFichaLoading] = useState(false);

  // Cargar pines de organizaciones
  useEffect(() => {
    if (mode === 'events') return;
    setPinsLoading(true);
    api.getMapaEcosistema(filters)
      .then((data) => setPins(data.pins))
      .catch(console.error)
      .finally(() => setPinsLoading(false));
  }, [filters, mode]);

  // Cargar pines de eventos cuando se activa ese modo
  useEffect(() => {
    if (mode !== 'events') return;
    setEventsLoading(true);
    api.getEventosMapa()
      .then(setEventPoints)
      .catch(console.error)
      .finally(() => setEventsLoading(false));
  }, [mode]);

  const handleModeChange = useCallback((newMode: MapMode) => {
    setMode(newMode);
    setModeMenuOpen(false);
    setFilters(EMPTY_FILTERS);
    setSelectedId(null);
    setFicha(null);
    setFilterOpen(false);
  }, []);

  // Abrir/cerrar menú de modo: cierra el de filtros y la ficha
  const handleToggleModeMenu = useCallback(() => {
    setModeMenuOpen((o) => !o);
    setFilterOpen(false);
    setSelectedId(null);
    setFicha(null);
  }, []);

  // Abrir/cerrar filtros: cierra el de modo y la ficha
  const handleToggleFilter = useCallback(() => {
    setFilterOpen((o) => !o);
    setModeMenuOpen(false);
    setSelectedId(null);
    setFicha(null);
  }, []);

  const handleFilterChange = useCallback((key: keyof MapFilters, value: string | undefined) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  }, []);

  const handleClearFilters = useCallback(() => {
    setFilters(EMPTY_FILTERS);
  }, []);

  const handlePinClick = useCallback((id: number) => {
    if (mode !== 'pins') return;
    setSelectedId(id);
    setFicha(null);
    setFichaLoading(true);
    setFilterOpen(false);
    setModeMenuOpen(false);
    api.getFichaActor(id)
      .then(setFicha)
      .catch(console.error)
      .finally(() => setFichaLoading(false));
  }, [mode]);

  const handleCloseSheet = useCallback(() => {
    setSelectedId(null);
    setFicha(null);
  }, []);

  const modeLabel: Record<MapMode, { label: string; icon: React.ReactNode }> = {
    pins:     { label: 'Organizaciones', icon: <IconBuildingCommunity size={16} stroke={1.5} /> },
    heatmap:  { label: 'Mapa de calor',  icon: <IconFlame size={16} stroke={1.5} /> },
    events:   { label: 'Eventos',         icon: <IconCalendarEvent size={16} stroke={1.5} /> },
  };

  const isLoading = mode === 'events' ? eventsLoading : pinsLoading;

  return (
    <div className={styles.page}>
      <PageHeader
        title="Mapa del Ecosistema"
        description="Visualización georreferenciada de actores STEM en Ciudad Juárez"
      />

      {/* Contenedor del mapa */}
      <div className={styles.mapContainer}>
        {/* Barra de controles sobre el mapa */}
        <div className={styles.controls}>
          {/* Dropdown de modo de visualización */}
          <div className={styles.modeWrapper}>
            <button className={styles.modeBtn} onClick={handleToggleModeMenu}>
              {modeLabel[mode].icon}
              {modeLabel[mode].label}
              {modeMenuOpen
                ? <IconChevronUp size={14} stroke={2} />
                : <IconChevronDown size={14} stroke={2} />}
            </button>

            {modeMenuOpen && (
              <div className={styles.modeMenu}>
                {(['pins', 'heatmap', 'events'] as MapMode[]).map((m) => (
                  <button
                    key={m}
                    className={`${styles.modeOption} ${mode === m ? styles.modeOptionActive : ''}`}
                    onClick={() => handleModeChange(m)}
                  >
                    {modeLabel[m].icon}
                    {modeLabel[m].label}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Filtros — solo en modo pins */}
          {mode === 'pins' && (
            <FilterPanel
              filters={filters}
              onChange={handleFilterChange}
              onClear={handleClearFilters}
              open={filterOpen}
              onToggle={handleToggleFilter}
            />
          )}
        </div>

        <EcosystemMap
          pins={pins}
          eventPoints={eventPoints}
          mode={mode}
          selectedId={selectedId}
          onPinClick={handlePinClick}
        />

        {/* Leyenda — solo en modo pins */}
        {mode === 'pins' && (
          <div className={styles.legend}>
            {TIPO_LEGEND.map((t) => (
              <div key={t.label} className={styles.legendItem}>
                <span className={styles.legendDot} style={{ background: t.color }} />
                <span className={styles.legendLabel}>{t.label}</span>
              </div>
            ))}
          </div>
        )}

        {/* Ficha actor */}
        {selectedId !== null && (
          <div className={styles.sheetOverlay}>
            <ActorSheet
              ficha={ficha}
              loading={fichaLoading}
              onClose={handleCloseSheet}
            />
          </div>
        )}

        {isLoading && (
          <div className={styles.loadingBadge}>
            {mode === 'events' ? 'Cargando eventos…' : 'Cargando actores…'}
          </div>
        )}
      </div>
    </div>
  );
}
