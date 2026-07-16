// -- Backend API consumption --

import axios from 'axios';
import type {
  PanoramaGeneralResponse,
  BeneficiariosResponse,
  InclusionResponse,
  OfertaSTEMResponse,
  MadurezResponse,
  MapaEcosistemaResponse,
  FichaActor,
  MapFilters,
  IndiceSaludResponse,
} from '../types';

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  timeout: 15_000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor de errores global
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ??
      error.message ??
      'Error de conexión con el servidor';
    console.error('[API Error]', message);
    return Promise.reject(new Error(message));
  }
);

// Endpoints por modulo

export const api = {

  // --- Panorama General ---
  getPanoramaGeneral: () =>
    client
      .get<PanoramaGeneralResponse>('/api/panorama_general')
      .then((r) => r.data),

  // --- Perfil de Beneficiarios ---
  getBeneficiarios: () =>
    client
      .get<BeneficiariosResponse>('/api/beneficiarios')
      .then((r) => r.data),

  // --- Inclusión y Género ---
  getInclusion: () =>
    client
      .get<InclusionResponse>('/api/inclusion')
      .then((r) => r.data),

  // --- Oferta STEM ---
  getOfertaSTEM: () =>
    client
      .get<OfertaSTEMResponse>('/api/oferta_stem')
      .then((r) => r.data),

  // --- Madurez del Ecosistema ---
  getMadurez: () =>
    client
      .get<MadurezResponse>('/api/madurez_ecosistema')
      .then((r) => r.data),

  // --- Mapa del Ecosistema ---
  getMapaEcosistema: (filters?: MapFilters) =>
    client
      .get<MapaEcosistemaResponse>('/api/mapa_ecosistema/', { params: filters })
      .then((r) => r.data),
 
  getFichaActor: (orgId: number) =>
    client
      .get<FichaActor>(`/api/mapa_ecosistema/actor/${orgId}`)
      .then((r) => r.data),
  
  // --- Índice de Salud del Ecosistema ---
  getIndiceSalud: () =>
    client
      .get<IndiceSaludResponse>('/api/indice_salud/indice-salud')
      .then((r) => r.data),

  // --- Eventos ---
  getEventosProximos: (fecha?: string) =>
    client
      .get<import('../types').Evento[]>('/api/eventos/proximos', { params: fecha ? { fecha } : {} })
      .then((r) => r.data),

  getEventosHistorial: (params?: { skip?: number; limit?: number; organizacion_id?: number; tipo?: string; enfoque?: string }) =>
    client
      .get<import('../types').Evento[]>('/api/eventos/historial', { params })
      .then((r) => r.data),

  getEventosMapa: () =>
    client
      .get<import('../types').EventoMapPoint[]>('/api/eventos/mapa')
      .then((r) => r.data),

};
