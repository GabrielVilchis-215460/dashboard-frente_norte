/**
 * Capa de servicio — toda comunicación con el backend pasa por aquí.
 * Si el backend cambia de URL o se agrega autenticación, solo se toca este archivo.
 */
import axios from 'axios';
import type {
  Organizacion, OrganizacionMapPin, Programa,
  PanoramaGeneral, PerfilBeneficiarios, InclusionFemenina,
  OfertaSTEM, MadurezEcosistema, CoberturaTerritorial, IndiceSaludEcosistema,
} from '../types';

const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1';
const api = axios.create({ baseURL: BASE });

// ── Organizaciones ────────────────────────────────────────────
export const getOrganizaciones = (params?: Record<string, string>) =>
  api.get<Organizacion[]>('/organizaciones', { params }).then(r => r.data);

export const getOrganizacionesMapa = (params?: Record<string, string>) =>
  api.get<OrganizacionMapPin[]>('/organizaciones/mapa', { params }).then(r => r.data);

export const getOrganizacion = (id: number) =>
  api.get<Organizacion>(`/organizaciones/${id}`).then(r => r.data);

// ── Programas ─────────────────────────────────────────────────
export const getProgramas = (params?: Record<string, string>) =>
  api.get<Programa[]>('/programas', { params }).then(r => r.data);

// ── Métricas del dashboard ────────────────────────────────────
export const getPanorama = () =>
  api.get<PanoramaGeneral>('/metricas/panorama').then(r => r.data);

export const getBeneficiarios = () =>
  api.get<PerfilBeneficiarios>('/metricas/beneficiarios').then(r => r.data);

export const getInclusionFemenina = () =>
  api.get<InclusionFemenina>('/metricas/inclusion').then(r => r.data);

export const getOfertaSTEM = () =>
  api.get<OfertaSTEM>('/metricas/oferta').then(r => r.data);

export const getMadurez = () =>
  api.get<MadurezEcosistema>('/metricas/madurez').then(r => r.data);

export const getCobertura = () =>
  api.get<CoberturaTerritorial>('/metricas/cobertura').then(r => r.data);

export const getIndiceSalud = () =>
  api.get<IndiceSaludEcosistema>('/metricas/indice-salud').then(r => r.data);
