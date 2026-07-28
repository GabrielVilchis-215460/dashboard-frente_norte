// -- Fuente para el Sidebar

import { ROUTES } from './routes';

export interface NavItem {
  key: string;
  label: string;
  path: string;
  icon: string; // Nombre del icono de tabler
}

export const NAV_ITEMS: NavItem[] = [
  {
    key: 'overview',
    label: 'Panorama General',
    path: ROUTES.OVERVIEW,
    icon: 'IconChartBar',
  },
  {
    key: 'beneficiaries',
    label: 'Perfil de Beneficiarios',
    path: ROUTES.BENEFICIARIES,
    icon: 'IconUsers',
  },
  {
    key: 'inclusion',
    label: 'Inclusión y Género',
    path: ROUTES.INCLUSION,
    icon: 'IconVenus',
  },
  {
    key: 'stem-offer',
    label: 'Oferta STEM',
    path: ROUTES.STEM_OFFER,
    icon: 'IconFlask',
  },
  {
    key: 'maturity',
    label: 'Madurez del Ecosistema',
    path: ROUTES.MATURITY,
    icon: 'IconTrendingUp',
  },
  {
    key: 'map',
    label: 'Mapa del Ecosistema',
    path: ROUTES.MAP,
    icon: 'IconMap',
  },
  {
    key: 'health',
    label: 'Índice de Salud',
    path: ROUTES.HEALTH,
    icon: 'IconActivity',
  },
  {
    key: 'events',
    label: 'Eventos',
    path: ROUTES.EVENTS,
    icon: 'IconCalendarEvent',
  },
];

export const ADMIN_NAV_ITEM: NavItem = {
  key: 'admin',
  label: 'Administración',
  path: ROUTES.ADMIN,
  icon: 'IconSettings',
};
