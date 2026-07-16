// -- Admin API: auth + CRUD de organizaciones y programas --

import axios from 'axios';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface Organizacion {
  id: number;
  nombre: string;
  tipo: string;
  areas_stem: string[];
  enfoque_principal?: string;
  descripcion?: string;
  logo_url?: string;
  contacto_nombre?: string;
  contacto_email?: string;
  contacto_telefono?: string;
  sitio_web?: string;
  latitud?: number;
  longitud?: number;
  direccion?: string;
  zona?: string;
  colonias: string[];
  activo: boolean;
  fuente?: string;
  created_at?: string;
  updated_at?: string;
}

export interface OrganizacionCreate extends Omit<Organizacion, 'id' | 'created_at' | 'updated_at'> {}

export interface Programa {
  id: number;
  nombre?: string;
  organizacion_id: number;
  descripcion?: string;
  areas_stem: string[];
  tipos_actividad: string[];
  modalidad?: string;
  poblacion_objetivo?: string;
  nivel_educativo?: string;
  pct_mujeres_rango?: string;
  pct_mujeres_min?: number;
  pct_mujeres_max?: number;
  pct_mujeres_mid?: number;
  zona?: string;
  colonias_impacto: string[];
  volumen_semestral?: string;
  volumen_min?: number;
  volumen_max?: number;
  volumen_mid?: number;
  temporalidad?: string;
  madurez?: string;
  casos_exito?: string;
  siguiente_paso?: string;
  activo: boolean;
  fuente?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ProgramaCreate extends Omit<Programa, 'id' | 'created_at' | 'updated_at'> {}

const TOKEN_KEY = 'admin_token';

export const authStorage = {
  getToken: () => sessionStorage.getItem(TOKEN_KEY),
  setToken: (token: string) => sessionStorage.setItem(TOKEN_KEY, token),
  clearToken: () => sessionStorage.removeItem(TOKEN_KEY),
};

const adminClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  timeout: 15_000,
  headers: { 'Content-Type': 'application/json' },
});

// Inyectar token en cada request
adminClient.interceptors.request.use((config) => {
  const token = authStorage.getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Redirigir a /admin/login en 401
adminClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authStorage.clearToken();
      window.location.href = '/admin/login';
    }
    const message =
      error.code === 'ECONNABORTED'
        ? 'El servidor tardó demasiado en responder. Intenta de nuevo.'
        : error.response?.data?.detail ?? error.message ?? 'Error de conexión';
    return Promise.reject(new Error(message));
  }
);

export const adminApi = {
  // Auth
  login: (data: LoginRequest) =>
    adminClient.post<TokenResponse>('/api/auth/login', data).then((r) => r.data),

  // Organizaciones
  getOrganizaciones: () =>
    adminClient.get<Organizacion[]>('/api/panel_admin/organizaciones').then((r) => r.data),

  createOrganizacion: (data: OrganizacionCreate) =>
    adminClient.post<Organizacion>('/api/panel_admin/organizaciones/create', data).then((r) => r.data),

  updateOrganizacion: (id: number, data: Partial<OrganizacionCreate>) =>
    adminClient.put<Organizacion>(`/api/panel_admin/organizaciones/${id}`, data).then((r) => r.data),

  toggleOrganizacion: (id: number) =>
    adminClient.patch<Organizacion>(`/api/panel_admin/organizaciones/${id}/toggle`).then((r) => r.data),

  // Programas
  getProgramas: () =>
    adminClient.get<Programa[]>('/api/panel_admin/programas').then((r) => r.data),

  createPrograma: (data: ProgramaCreate) =>
    adminClient.post<Programa>('/api/panel_admin/programas/create', data).then((r) => r.data),

  updatePrograma: (id: number, data: Partial<ProgramaCreate>) =>
    adminClient.put<Programa>(`/api/panel_admin/programas/${id}`, data).then((r) => r.data),

  togglePrograma: (id: number) =>
    adminClient.patch<Programa>(`/api/panel_admin/programas/${id}/toggle`).then((r) => r.data),

  // Exportación CSV (requiere JWT — se inyecta automáticamente)
  exportOrganizaciones: async () => {
    const res = await adminClient.get('/api/exportar/organizaciones', { responseType: 'blob' });
    const url = URL.createObjectURL(new Blob([res.data], { type: 'text/csv' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = 'organizaciones.csv';
    a.click();
    URL.revokeObjectURL(url);
  },

  exportProgramas: async () => {
    const res = await adminClient.get('/api/exportar/programas', { responseType: 'blob' });
    const url = URL.createObjectURL(new Blob([res.data], { type: 'text/csv' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = 'programas.csv';
    a.click();
    URL.revokeObjectURL(url);
  },

  // Eventos
  getEventosAdmin: (params?: { solo_activos?: boolean; organizacion_id?: number }) =>
    adminClient.get<import('../types').Evento[]>('/api/eventos/admin/todos', { params }).then((r) => r.data),

  createEvento: (data: import('../types').EventoCreate) =>
    adminClient.post<import('../types').Evento>('/api/eventos/admin', data).then((r) => r.data),

  updateEvento: (id: number, data: import('../types').EventoUpdate) =>
    adminClient.put<import('../types').Evento>(`/api/eventos/admin/${id}`, data).then((r) => r.data),

  toggleEvento: (id: number) =>
    adminClient.patch<import('../types').Evento>(`/api/eventos/admin/${id}/toggle`).then((r) => r.data),

  uploadImagenEvento: async (file: File): Promise<string> => {
    const form = new FormData();
    form.append('file', file);
    const res = await adminClient.post<{ url: string }>('/api/eventos/admin/upload-imagen', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data.url;
  },
};
