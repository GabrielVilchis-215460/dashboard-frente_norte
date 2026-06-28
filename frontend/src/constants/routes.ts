// -- Constantes de rutas --

export const ROUTES = {
  OVERVIEW:       '/',
  BENEFICIARIES:  '/beneficiarios',
  INCLUSION:      '/inclusion',
  STEM_OFFER:     '/oferta-stem',
  MATURITY:       '/madurez',
  MAP:            '/mapa',
  GAPS:           '/brechas',
  ADMIN:          '/admin',
} as const;

export type RouteKey = keyof typeof ROUTES;
export type RoutePath = typeof ROUTES[RouteKey];
