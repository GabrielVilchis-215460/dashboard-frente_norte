// -- Backend API consumption --

import axios from 'axios';
import type {
  PanoramaGeneralResponse,
  BeneficiariosResponse,
  InclusionResponse,
  OfertaSTEMResponse,
  MadurezResponse,
  MapaEcosistemaResponse,
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
      .get<PanoramaGeneralResponse>('/dashboard/panorama-general')
      .then((r) => r.data),

  // --- Perfil de Beneficiarios ---
  getBeneficiarios: () =>
    client
      .get<BeneficiariosResponse>('/dashboard/beneficiarios')
      .then((r) => r.data),

  // --- Inclusión y Género ---
  getInclusion: () =>
    client
      .get<InclusionResponse>('/dashboard/inclusion')
      .then((r) => r.data),

  // --- Oferta STEM ---
  getOfertaSTEM: () =>
    client
      .get<OfertaSTEMResponse>('/dashboard/oferta-stem')
      .then((r) => r.data),

  // --- Madurez del Ecosistema ---
  getMadurez: () =>
    client
      .get<MadurezResponse>('/dashboard/madurez')
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
      .get<MapaEcosistemaResponse>('/dashboard/mapa', { params: filters })
      .then((r) => r.data),
};
