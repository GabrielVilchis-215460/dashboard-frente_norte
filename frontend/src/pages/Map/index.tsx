// Mapa del Ecosistema

import { useState, useCallback, useEffect } from 'react';
import {
  IconBuildingCommunity,
  IconFlame,
  IconChevronDown,
  IconChevronUp,
} from '@tabler/icons-react';
import { PageHeader } from '../../components/layout';
import { api } from '../../services/api';
import type { MapFilters, FichaActor } from '../../types';
import { EcosystemMap } from './components/EcosystemMap';
import { FilterPanel } from './components/FilterPanel';
import { ActorSheet } from './components/ActorSheet';
import { TIPO_LEGEND } from './components/mapConfig';
import styles from './Map.module.css';

type ViewMode = 'pins' | 'heatmap';

const EMPTY_FILTERS: MapFilters = { solo_con_coordenadas: true };

export function MapPage() {
  const [filters, setFilters] = useState<MapFilters>(EMPTY_FILTERS);
  const [mode, setMode] = useState<ViewMode>('pins');
  const [filterOpen, setFilterOpen] = useState(false);
  const [modeMenuOpen, setModeMenuOpen] = useState(false);

  const [pins, setPins] = useState<any[]>([]);
  const [pinsLoading, setPinsLoading] = useState(true);

  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [ficha, setFicha] = useState<FichaActor | null>(null);
  const [fichaLoading, setFichaLoading] = useState(false);

  // Cargar pines cuando cambian los filtros
  useEffect(() => {
    setPinsLoading(true);
    api.getMapaEcosistema(filters)
      .then((data) => setPins(data.pins))
      .catch(console.error)
      .finally(() => setPinsLoading(false));
  }, [filters]);

  // Cambiar modo: limpiar filtros y cerrar todo
  const handleModeChange = useCallback((newMode: ViewMode) => {
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

  // Click en pin: cierra menús abiertos
  const handlePinClick = useCallback((id: number) => {
    setSelectedId(id);
    setFicha(null);
    setFichaLoading(true);
    setFilterOpen(false);
    setModeMenuOpen(false);
    api.getFichaActor(id)
      .then(setFicha)
      .catch(console.error)
      .finally(() => setFichaLoading(false));
  }, []);

  const handleCloseSheet = useCallback(() => {
    setSelectedId(null);
    setFicha(null);
  }, []);

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
              {mode === 'pins'
                ? <><IconBuildingCommunity size={16} stroke={1.5} /> Organizaciones</>
                : <><IconFlame size={16} stroke={1.5} /> Mapa de calor</>
              }
              {modeMenuOpen
                ? <IconChevronUp size={14} stroke={2} />
                : <IconChevronDown size={14} stroke={2} />
              }
            </button>

            {modeMenuOpen && (
              <div className={styles.modeMenu}>
                <button
                  className={`${styles.modeOption} ${mode === 'pins' ? styles.modeOptionActive : ''}`}
                  onClick={() => handleModeChange('pins')}
                >
                  <IconBuildingCommunity size={16} stroke={1.5} />
                  Organizaciones
                </button>
                <button
                  className={`${styles.modeOption} ${mode === 'heatmap' ? styles.modeOptionActive : ''}`}
                  onClick={() => handleModeChange('heatmap')}
                >
                  <IconFlame size={16} stroke={1.5} />
                  Mapa de calor
                </button>
              </div>
            )}
          </div>

          {/* Panel de filtros */}
          <FilterPanel
            filters={filters}
            onChange={handleFilterChange}
            onClear={handleClearFilters}
            open={filterOpen}
            onToggle={handleToggleFilter}
          />
        </div>

        {/* Mapa */}
        <EcosystemMap
          pins={pins}
          mode={mode}
          selectedId={selectedId}
          onPinClick={handlePinClick}
        />

        {/* Leyenda de tipos (solo en modo pines) */}
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

        {/* Ficha del actor — overlay sobre el mapa, abajo a la izquierda */}
        {(selectedId !== null) && (
          <div className={styles.sheetOverlay}>
            <ActorSheet
              ficha={ficha}
              loading={fichaLoading}
              onClose={handleCloseSheet}
            />
          </div>
        )}

        {/* Indicador de carga de pines */}
        {pinsLoading && (
          <div className={styles.loadingBadge}>Cargando actores…</div>
        )}
      </div>
    </div>
  );
}
