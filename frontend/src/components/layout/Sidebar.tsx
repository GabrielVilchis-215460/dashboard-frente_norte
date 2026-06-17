// Sidebar de navegación — refleja los 8 módulos del dashboard
// según la ficha técnica del PDF de Frente Norte
import { NavLink } from 'react-router-dom';

const MODULOS = [
  { path: '/',              label: 'Panorama General',        icon: '📊' },
  { path: '/beneficiarios', label: 'Perfil de Beneficiarios', icon: '👥' },
  { path: '/inclusion',     label: 'Inclusión y Género',      icon: '♀' },
  { path: '/oferta',        label: 'Oferta STEM',             icon: '🔬' },
  { path: '/madurez',       label: 'Madurez del Ecosistema',  icon: '📈' },
  { path: '/cobertura',     label: 'Cobertura Territorial',   icon: '🗺' },
  { path: '/mapa',          label: 'Mapa del Ecosistema',     icon: '📍' },
  { path: '/indice',        label: 'Índice de Salud',         icon: '💡' },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span>Frente Norte</span>
        <small>Ecosistema STEM · CJ</small>
      </div>
      <nav>
        {MODULOS.map(m => (
          <NavLink key={m.path} to={m.path} end={m.path === '/'}>
            <span>{m.icon}</span>
            <span>{m.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
