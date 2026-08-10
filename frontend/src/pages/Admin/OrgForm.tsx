import { useState } from 'react';
import styles from './AdminForm.module.css';
import { LocationPicker } from './LocationPicker';
import { adminApi } from '../../services/adminApi';
import type { Organizacion, OrganizacionCreate } from '../../services/adminApi';

const TIPOS = [
  'ONG / Asociación Civil',
  'OSC / Sociedad Civil',
  'Institución Educativa',
  'Empresa Tecnológica',
  'Centro de Investigación',
  'Entidad Gubernamental',
  'Makerspace / Laboratorio',
  'Organismo Articulador',
  'Organismo Financiador',
  'Programa / Iniciativa',
];

const AREAS = [
  'Ciencia',
  'Tecnología',
  'Ingeniería',
  'Matemáticas',
  'Robótica',
  'Electrónica',
  'Inteligencia Artificial',
  'Diseño',
  'Medio ambiente',
  'Energía',
  'Historia natural',
  'Articulación / políticas públicas',
  'Emprendimiento / Innovación económica',
  'Desarrollo comunitario',
];

const ZONAS = ['Urbana', 'Rural', 'Ambas'];
const ENFOQUES = ['Educación / Capacitación técnica', 'Investigación / Desarrollo', 'Articulación y políticas públicas', 'Incubación / Aceleración'];

type FormData = Omit<OrganizacionCreate, 'tipo' | 'areas_stem' | 'colonias'> & {
  tipo: string[];
  areas_stem: string[];
  colonias: string[];
};

interface OrgFormProps {
  value: FormData;
  onChange: (v: FormData) => void;
}

function toggleItem(arr: string[], item: string): string[] {
  return arr.includes(item) ? arr.filter((x) => x !== item) : [...arr, item];
}

export function OrgForm({ value, onChange }: OrgFormProps) {
  const set = (key: keyof FormData, val: unknown) => onChange({ ...value, [key]: val });

  const [mapsUrl, setMapsUrl] = useState('');
  const [parseando, setParseando] = useState(false);
  const [urlError, setUrlError] = useState('');

  async function handleExtraerCoords() {
    if (!mapsUrl.trim()) return;
    setParseando(true);
    setUrlError('');
    try {
      const { latitud, longitud } = await adminApi.parseGoogleMapsUrl(mapsUrl);
      onChange({ ...value, latitud, longitud });
    } catch (err) {
      setUrlError(err instanceof Error ? err.message : 'No se pudo procesar el link.');
    } finally {
      setParseando(false);
    }
  }

  return (
    <div className={styles.grid}>
      <div className={`${styles.fieldGroup} ${styles.fullWidth}`}>
        <label className={styles.label}>Nombre *</label>
        <input className={styles.input} value={value.nombre ?? ''} onChange={(e) => set('nombre', e.target.value)} placeholder="Nombre de la organización" required />
      </div>

      <span className={styles.sectionTitle}>Tipos de Organización *</span>
      {TIPOS.map((t) => (
        <label key={t} className={styles.checkboxRow}>
          <input 
            type="checkbox" 
            checked={Array.isArray(value.tipo) && value.tipo.includes(t)} 
            onChange={() => set('tipo', toggleItem(value.tipo || [], t))} 
          />
          <span>{t}</span>
        </label>
      ))}

      <div className={styles.fieldGroup} style={{ marginTop: '16px' }}>
        <label className={styles.label}>Zona</label>
        <select className={styles.select} value={value.zona ?? ''} onChange={(e) => set('zona', e.target.value)}>
          <option value="">Seleccionar...</option>
          {ZONAS.map((z) => <option key={z} value={z}>{z}</option>)}
        </select>
      </div>

      <div className={styles.fieldGroup}>
        <label className={styles.label}>Enfoque principal</label>
        <select className={styles.select} value={value.enfoque_principal ?? ''} onChange={(e) => set('enfoque_principal', e.target.value)}>
          <option value="">Seleccionar...</option>
          {ENFOQUES.map((e) => <option key={e} value={e}>{e}</option>)}
        </select>
      </div>

      <div className={styles.fieldGroup}>
        <label className={styles.label}>Fuente</label>
        <select className={styles.select} value={value.fuente ?? ''} onChange={(e) => set('fuente', e.target.value)}>
          <option value="">Seleccionar...</option>
          <option value="encuesta">Encuesta</option>
          <option value="investigacion_documental">Investigación documental</option>
          <option value="manual">Manual</option>
        </select>
      </div>

      <span className={styles.sectionTitle}>Áreas STEM</span>
      {AREAS.map((area) => (
        <label key={area} className={styles.checkboxRow}>
          <input type="checkbox" checked={value.areas_stem.includes(area)} onChange={() => set('areas_stem', toggleItem(value.areas_stem, area))} />
          <span>{area}</span>
        </label>
      ))}

      <span className={styles.sectionTitle}>Descripción</span>
      <div className={`${styles.fieldGroup} ${styles.fullWidth}`}>
        <textarea className={styles.textarea} value={value.descripcion ?? ''} onChange={(e) => set('descripcion', e.target.value)} placeholder="Descripción breve de la organización" />
      </div>

      <span className={styles.sectionTitle}>Contacto</span>
      <div className={styles.fieldGroup}>
        <label className={styles.label}>Nombre contacto</label>
        <input className={styles.input} value={value.contacto_nombre ?? ''} onChange={(e) => set('contacto_nombre', e.target.value)} />
      </div>
      <div className={styles.fieldGroup}>
        <label className={styles.label}>Email</label>
        <input className={styles.input} type="email" value={value.contacto_email ?? ''} onChange={(e) => set('contacto_email', e.target.value)} />
      </div>
      <div className={styles.fieldGroup}>
        <label className={styles.label}>Teléfono</label>
        <input className={styles.input} value={value.contacto_telefono ?? ''} onChange={(e) => set('contacto_telefono', e.target.value)} />
      </div>
      <div className={styles.fieldGroup}>
        <label className={styles.label}>Sitio web</label>
        <input className={styles.input} type="url" value={value.sitio_web ?? ''} onChange={(e) => set('sitio_web', e.target.value)} placeholder="https://..." />
      </div>

      <span className={styles.sectionTitle}>Geolocalización</span>

      <div className={`${styles.fieldGroup} ${styles.fullWidth}`}>
        <label className={styles.label}>Link de Google Maps</label>
        <div style={{ display: 'flex', gap: 8 }}>
          <input
            className={styles.input}
            value={mapsUrl}
            onChange={(e) => setMapsUrl(e.target.value)}
            placeholder="Pega el link de Google Maps aquí"
          />
          <button type="button" onClick={handleExtraerCoords} disabled={parseando || !mapsUrl.trim()}>
            {parseando ? 'Buscando...' : 'Extraer coordenadas'}
          </button>
        </div>
        {urlError && <span className={styles.errorText}>{urlError}</span>}
      </div>

      <div className={styles.fullWidth}>
        <LocationPicker
          latitud={value.latitud}
          longitud={value.longitud}
          onChange={(lat, lng) => onChange({ ...value, latitud: lat, longitud: lng })}
          readOnly
        />
      </div>
      <div className={`${styles.fieldGroup} ${styles.fullWidth}`}>
        <label className={styles.label}>Dirección</label>
        <input className={styles.input} value={value.direccion ?? ''} onChange={(e) => set('direccion', e.target.value)} />
      </div>

      <label className={styles.checkboxRow}>
        <input type="checkbox" checked={value.activo} onChange={(e) => set('activo', e.target.checked)} />
        <span>Organización activa</span>
      </label>
    </div>
  );
}

export function defaultOrg(): FormData {
  return {
    nombre: '',
    tipo: [],
    areas_stem: [],
    enfoque_principal: undefined,
    descripcion: undefined,
    logo_url: undefined,
    contacto_nombre: undefined,
    contacto_email: undefined,
    contacto_telefono: undefined,
    sitio_web: undefined,
    latitud: undefined,
    longitud: undefined,
    direccion: undefined,
    zona: undefined,
    colonias: [],
    activo: true,
    fuente: undefined,
  };
}

export function orgToForm(org: Organizacion): FormData {
  return {
    nombre: org.nombre,
    tipo: Array.isArray(org.tipo) ? org.tipo : (org.tipo ? [org.tipo] : []),
    areas_stem: org.areas_stem ?? [],
    enfoque_principal: org.enfoque_principal,
    descripcion: org.descripcion,
    logo_url: org.logo_url,
    contacto_nombre: org.contacto_nombre,
    contacto_email: org.contacto_email,
    contacto_telefono: org.contacto_telefono,
    sitio_web: org.sitio_web,
    latitud: org.latitud,
    longitud: org.longitud,
    direccion: org.direccion,
    zona: org.zona,
    colonias: org.colonias ?? [],
    activo: org.activo,
    fuente: org.fuente,
  };
}