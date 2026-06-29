// -- Backend API consumption --

import axios from 'axios';
import type {
  PanoramaGeneralResponse,
  BeneficiariosResponse,
  InclusionResponse,
  OfertaSTEMResponse,
  MadurezResponse,
  MapaEcosistemaResponse,
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
  getMapaEcosistema: (filters?: {
    tipo?: string;
    area?: string;
    nivel_educativo?: string;
    zona?: string;
    madurez?: string;
  }) =>
    client
      .get<MapaEcosistemaResponse>('/api/mapa_ecosistema', { params: filters })
      .then((r) => r.data),
  
  // --- Índice de Salud del Ecosistema ---
  getIndiceSalud: () =>
    client
      .get<IndiceSaludResponse>('/api/indice_salud/indice-salud')
      .then((r) => r.data),

};
