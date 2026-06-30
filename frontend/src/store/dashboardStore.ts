// -- Estado compartido entre paginas --

import { create } from 'zustand';

interface DashboardStore {
  // Última actualización global
  lastUpdated: string | null;
  setLastUpdated: (date: string) => void;

  // Filtros globales del mapa (?
  mapFilters: {
    tipo?: string;
    area?: string;
    zona?: string;
    madurez?: string;
  };
  setMapFilter: (key: string, value: string | undefined) => void;
  clearMapFilters: () => void;
}

export const useDashboardStore = create<DashboardStore>((set) => ({
  lastUpdated: null,
  setLastUpdated: (date) => set({ lastUpdated: date }),

  mapFilters: {},
  setMapFilter: (key, value) =>
    set((state) => ({
      mapFilters: { ...state.mapFilters, [key]: value },
    })),
  clearMapFilters: () => set({ mapFilters: {} }),
}));
