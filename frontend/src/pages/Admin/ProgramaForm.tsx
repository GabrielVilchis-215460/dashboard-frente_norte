import styles from './AdminForm.module.css';
import type { Programa, ProgramaCreate, Organizacion } from '../../services/adminApi';

const AREAS = ['Ciencia', 'Tecnología', 'Ingeniería', 'Matemáticas', 'Robótica', 'IA', 'Medio ambiente', 'Historia Natural'];
const TIPOS_ACTIVIDAD = ['Talleres/Cursos/Bootcamps', 'Eventos/Conferencias', 'Mentorías/Programas de largo plazo', 'Incubación/Aceleración', 'Investigación/Proyectos', 'Visualización/Divulgación'];
const MODALIDADES = ['Presencial', 'Virtual', 'Híbrido'];
const POBLACIONES = ['Niñez (6-12)', 'Adolescentes (13-17)', 'Jóvenes', 'Profesionistas/Docentes/Emprendedores', 'Público general'];
const NIVELES = ['Preescolar', 'Primaria', 'Secundaria', 'Preparatoria', 'Superior', 'Público general'];
const MADURECES = ['Exploración', 'Implementación', 'Escalamiento'];
const ZONAS = ['Urbana', 'Rural', 'Ambas'];

type FormData = Omit<ProgramaCreate, 'areas_stem' | 'tipos_actividad' | 'colonias_impacto'> & {
  areas_stem: string[];
  tipos_actividad: string[];
  colonias_impacto: string[];
};

interface ProgramaFormProps {
  value: FormData;
  onChange: (v: FormData) => void;
  organizaciones: Organizacion[];
}

function toggleItem(arr: string[], item: string): string[] {
  return arr.includes(item) ? arr.filter((x) => x !== item) : [...arr, item];
}

export function ProgramaForm({ value, onChange, organizaciones }: ProgramaFormProps) {
  const set = (key: keyof FormData, val: unknown) => onChange({ ...value, [key]: val });

  return (
    <div className={styles.grid}>
      <div className={styles.fieldGroup}>
        <label className={styles.label}>Organización *</label>
        <select className={styles.select} value={value.organizacion_id ?? ''} onChange={(e) => set('organizacion_id', parseInt(e.target.value))}>
          <option value="">Seleccionar...</option>
          {organizaciones.map((o) => <option key={o.id} value={o.id}>{o.nombre}</option>)}
        </select>
      </div>

      <div className={styles.fieldGroup}>
        <label className={styles.label}>Nombre del programa</label>
        <input className={styles.input} value={value.nombre ?? ''} onChange={(e) => set('nombre', e.target.value)} placeholder="Nombre del programa" />
      </div>

      <div className={styles.fieldGroup}>
        <label className={styles.label}>Modalidad</label>
        <select className={styles.select} value={value.modalidad ?? ''} onChange={(e) => set('modalidad', e.target.value)}>
          <option value="">Seleccionar...</option>
          {MODALIDADES.map((m) => <option key={m} value={m}>{m}</option>)}
        </select>
      </div>

      <div className={styles.fieldGroup}>
        <label className={styles.label}>Madurez</label>
        <select className={styles.select} value={value.madurez ?? ''} onChange={(e) => set('madurez', e.target.value)}>
          <option value="">Seleccionar...</option>
          {MADURECES.map((m) => <option key={m} value={m}>{m}</option>)}
        </select>
      </div>

      <div className={styles.fieldGroup}>
        <label className={styles.label}>Población objetivo</label>
        <select className={styles.select} value={value.poblacion_objetivo ?? ''} onChange={(e) => set('poblacion_objetivo', e.target.value)}>
          <option value="">Seleccionar...</option>
          {POBLACIONES.map((p) => <option key={p} value={p}>{p}</option>)}
        </select>
      </div>

      <div className={styles.fieldGroup}>
        <label className={styles.label}>Nivel educativo</label>
        <select className={styles.select} value={value.nivel_educativo ?? ''} onChange={(e) => set('nivel_educativo', e.target.value)}>
          <option value="">Seleccionar...</option>
          {NIVELES.map((n) => <option key={n} value={n}>{n}</option>)}
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
        <label className={styles.label}>Temporalidad</label>
        <input className={styles.input} value={value.temporalidad ?? ''} onChange={(e) => set('temporalidad', e.target.value)} placeholder="Anual / Semestral / ..." />
      </div>

      <span className={styles.sectionTitle}>Áreas STEM</span>
      {AREAS.map((area) => (
        <label key={area} className={styles.checkboxRow}>
          <input type="checkbox" checked={value.areas_stem.includes(area)} onChange={() => set('areas_stem', toggleItem(value.areas_stem, area))} />
          <span>{area}</span>
        </label>
      ))}

      <span className={styles.sectionTitle}>Tipos de actividad</span>
      {TIPOS_ACTIVIDAD.map((t) => (
        <label key={t} className={`${styles.checkboxRow} ${styles.fullWidth}`}>
          <input type="checkbox" checked={value.tipos_actividad.includes(t)} onChange={() => set('tipos_actividad', toggleItem(value.tipos_actividad, t))} />
          <span>{t}</span>
        </label>
      ))}

      <span className={styles.sectionTitle}>Participación femenina</span>
      <div className={styles.fieldGroup}>
        <label className={styles.label}>Rango (ej: 51-75)</label>
        <input className={styles.input} value={value.pct_mujeres_rango ?? ''} onChange={(e) => set('pct_mujeres_rango', e.target.value)} placeholder="0-25 / 26-50 / 51-75 / 76-100" />
      </div>
      <div className={styles.fieldGroup}>
        <label className={styles.label}>% mujeres promedio</label>
        <input className={styles.input} type="number" min="0" max="100" step="0.1" value={value.pct_mujeres_mid ?? ''} onChange={(e) => set('pct_mujeres_mid', e.target.value ? parseFloat(e.target.value) : undefined)} />
      </div>

      <span className={styles.sectionTitle}>Volumen semestral</span>
      <div className={styles.fieldGroup}>
        <label className={styles.label}>Rango (ej: 51-200)</label>
        <input className={styles.input} value={value.volumen_semestral ?? ''} onChange={(e) => set('volumen_semestral', e.target.value)} />
      </div>
      <div className={styles.fieldGroup}>
        <label className={styles.label}>Promedio beneficiarios</label>
        <input className={styles.input} type="number" value={value.volumen_mid ?? ''} onChange={(e) => set('volumen_mid', e.target.value ? parseInt(e.target.value) : undefined)} />
      </div>

      <span className={styles.sectionTitle}>Notas adicionales</span>
      <div className={`${styles.fieldGroup} ${styles.fullWidth}`}>
        <label className={styles.label}>Descripción</label>
        <textarea className={styles.textarea} value={value.descripcion ?? ''} onChange={(e) => set('descripcion', e.target.value)} />
      </div>
      <div className={`${styles.fieldGroup} ${styles.fullWidth}`}>
        <label className={styles.label}>Casos de éxito</label>
        <textarea className={styles.textarea} value={value.casos_exito ?? ''} onChange={(e) => set('casos_exito', e.target.value)} />
      </div>

      <label className={styles.checkboxRow}>
        <input type="checkbox" checked={value.activo} onChange={(e) => set('activo', e.target.checked)} />
        <span>Programa activo</span>
      </label>
    </div>
  );
}

export function defaultPrograma(orgId?: number): FormData {
  return {
    organizacion_id: orgId ?? 0,
    nombre: undefined,
    descripcion: undefined,
    areas_stem: [],
    tipos_actividad: [],
    modalidad: undefined,
    poblacion_objetivo: undefined,
    nivel_educativo: undefined,
    pct_mujeres_rango: undefined,
    pct_mujeres_min: undefined,
    pct_mujeres_max: undefined,
    pct_mujeres_mid: undefined,
    zona: undefined,
    colonias_impacto: [],
    volumen_semestral: undefined,
    volumen_min: undefined,
    volumen_max: undefined,
    volumen_mid: undefined,
    temporalidad: undefined,
    madurez: undefined,
    casos_exito: undefined,
    siguiente_paso: undefined,
    activo: true,
    fuente: undefined,
  };
}

export function programaToForm(p: Programa): FormData {
  return {
    organizacion_id: p.organizacion_id,
    nombre: p.nombre,
    descripcion: p.descripcion,
    areas_stem: p.areas_stem ?? [],
    tipos_actividad: p.tipos_actividad ?? [],
    modalidad: p.modalidad,
    poblacion_objetivo: p.poblacion_objetivo,
    nivel_educativo: p.nivel_educativo,
    pct_mujeres_rango: p.pct_mujeres_rango,
    pct_mujeres_min: p.pct_mujeres_min,
    pct_mujeres_max: p.pct_mujeres_max,
    pct_mujeres_mid: p.pct_mujeres_mid,
    zona: p.zona,
    colonias_impacto: p.colonias_impacto ?? [],
    volumen_semestral: p.volumen_semestral,
    volumen_min: p.volumen_min,
    volumen_max: p.volumen_max,
    volumen_mid: p.volumen_mid,
    temporalidad: p.temporalidad,
    madurez: p.madurez,
    casos_exito: p.casos_exito,
    siguiente_paso: p.siguiente_paso,
    activo: p.activo,
    fuente: p.fuente,
  };
}
