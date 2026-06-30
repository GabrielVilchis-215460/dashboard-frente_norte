import styles from './AdminForm.module.css';
import { LocationPicker } from './LocationPicker';
import type { Organizacion, OrganizacionCreate } from '../../services/adminApi';

const TIPOS = ['ONG / Asociación civil', 'Institución educativa', 'Gobierno', 'Empresa / Industria', 'Centro de investigación', 'Makerspace / Laboratorio', 'Centro comunitario', 'Incubadora / Aceleradora'];
const AREAS = ['Ciencia', 'Tecnología', 'Ingeniería', 'Matemáticas', 'Robótica', 'IA', 'Medio ambiente', 'Historia Natural'];
const ZONAS = ['Urbana', 'Rural', 'Ambas'];
const ENFOQUES = ['Educación / Capacitación técnica', 'Investigación / Desarrollo', 'Articulación y políticas públicas', 'Incubación / Aceleración'];

type FormData = Omit<OrganizacionCreate, 'areas_stem' | 'colonias'> & {
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

  return (
    <div className={styles.grid}>
      <div className={`${styles.fieldGroup} ${styles.fullWidth}`}>
        <label className={styles.label}>Nombre *</label>
        <input className={styles.input} value={value.nombre ?? ''} onChange={(e) => set('nombre', e.target.value)} placeholder="Nombre de la organización" required />
      </div>

      <div className={styles.fieldGroup}>
        <label className={styles.label}>Tipo *</label>
        <select className={styles.select} value={value.tipo ?? ''} onChange={(e) => set('tipo', e.target.value)}>
          <option value="">Seleccionar...</option>
          {TIPOS.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>

      <div className={styles.fieldGroup}>
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
      <div className={styles.fullWidth}>
        <LocationPicker
          latitud={value.latitud}
          longitud={value.longitud}
          onChange={(lat, lng) => onChange({ ...value, latitud: lat, longitud: lng })}
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
    tipo: '',
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
    tipo: org.tipo,
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
