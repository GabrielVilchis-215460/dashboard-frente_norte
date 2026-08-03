// -- Constantes de rutas --

export const ROUTES = {
  // Público
  HOME:           '/',
  EVENTS:         '/eventos',
  EVENT_DETAIL:   '/eventos/:id',
  ABOUT:          '/acerca-de',
  LOGIN:          '/login',

  // Dashboard (protegido — requiere sesión, viewer o admin)
  OVERVIEW:       '/dashboard',
  BENEFICIARIES:  '/dashboard/beneficiarios',
  INCLUSION:      '/dashboard/inclusion',
  STEM_OFFER:     '/dashboard/oferta-stem',
  MATURITY:       '/dashboard/madurez',
  MAP:            '/dashboard/mapa',
  HEALTH:         '/dashboard/salud',
  EVENTS_TAB:   '/dashboard/eventos',

  // Solo admin (CRUD)
  ADMIN:          '/dashboard/admin',
} as const;

export type RouteKey = keyof typeof ROUTES;
export type RoutePath = typeof ROUTES[RouteKey];

// Helper para armar el link de detalle de evento
export function eventDetailPath(id: number | string): string {
  return `/eventos/${id}`;
}