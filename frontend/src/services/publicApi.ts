// -- Consumo público del API de eventos (sin auth) --

import axios from 'axios';
import type { Evento, EventoMapPoint } from '../types';

const publicClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  timeout: 15_000,
  headers: { 'Content-Type': 'application/json' },
});

publicClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ??
      error.message ??
      'Error de conexión con el servidor';
    console.error('[API pública] Error', message);
    return Promise.reject(new Error(message));
  }
);

export interface EventosPublicoParams {
  q?: string;
  tipo?: string;
  enfoque?: string;
  orden?: 'recientes' | 'populares';
  skip?: number;
  limit?: number;
}

export interface EventosPublicoResponse {
  total: number;
  items: Evento[];
}

export const publicApi = {
  getEventosPublico: (params?: EventosPublicoParams) =>
    publicClient
      .get<EventosPublicoResponse>('/api/eventos/publico', { params })
      .then((r) => r.data),

  getEventoDetalle: (id: number | string) =>
    publicClient
      .get<Evento>(`/api/eventos/${id}`)
      .then((r) => r.data),

  getEventosMapa: () =>
    publicClient
      .get<EventoMapPoint[]>('/api/eventos/mapa')
      .then((r) => r.data),

  getEventosDestacados: (limit = 8) =>
    publicClient
      .get<EventosPublicoResponse>('/api/eventos/publico', { params: { limit } })
      .then((r) => r.data.items),
};