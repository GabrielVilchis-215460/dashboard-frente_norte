// Configuracion del mapa: Colores por tipo de org + opciones de filtros

export interface TipoConfig {
  label: string;
  color: string;
}

const TIPO_MAP: Array<{ keywords: string[]; config: TipoConfig }> = [
  {
    keywords: ['ong', 'asociacion', 'civil'],
    config: { label: 'ONG / Asociación Civil', color: '#38bdf8' },
  },
  {
    keywords: ['educativ', 'escuela', 'universidad', 'colegio', 'institucion'],
    config: { label: 'Institución Educativa', color: '#34d399' },
  },
  {
    keywords: ['empresa', 'tecnolog', 'tech', 'startup'],
    config: { label: 'Empresa Tecnológica', color: '#a78bfa' },
  },
  {
    keywords: ['investigacion', 'centro', 'research', 'lab'],
    config: { label: 'Centro de Investigación', color: '#fbbf24' },
  },
  {
    keywords: ['gobierno', 'municipal', 'estatal', 'federal', 'public'],
    config: { label: 'Gobierno', color: '#f87171' },
  },
  {
    keywords: ['maker', 'makerspace', 'laboratorio'],
    config: { label: 'Makerspace / Lab', color: '#2dd4bf' },
  },
];

const DEFAULT_CONFIG: TipoConfig = { label: 'Organización', color: '#94a3b8' };

function normalize(s: string): string {
  return s
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '');
}

export function getTipoConfig(tipo: string): TipoConfig {
  const norm = normalize(tipo);
  for (const entry of TIPO_MAP) {
    if (entry.keywords.some((kw) => norm.includes(kw))) {
      return entry.config;
    }
  }
  return DEFAULT_CONFIG;
}

// Legend derivada de TIPO_MAP para garantizar consistencia de colores
export const TIPO_LEGEND: TipoConfig[] = [
  ...TIPO_MAP.map((e) => e.config),
  DEFAULT_CONFIG,
];

// ----- Opciones de filtros -----

export interface FilterOption {
  label: string;
  value: string;
}

export interface FilterGroup {
  key: string;
  label: string;
  queryParam: string;
  options: FilterOption[];
}

export const FILTER_GROUPS: FilterGroup[] = [
  {
    key: 'tipo',
    label: 'Tipo de organización',
    queryParam: 'tipo',
    options: [
      { label: 'ONG / Asociación Civil', value: 'ONG / Asociación civil' },
      { label: 'Institución Educativa', value: 'Institución educativa' },
      { label: 'Empresa Tecnológica', value: 'Empresa tecnológica' },
      { label: 'Centro de Investigación', value: 'Centro de investigación' },
      { label: 'Gobierno', value: 'Gobierno' },
      { label: 'Makerspace / Lab', value: 'Makerspace' },
    ],
  },
  {
    key: 'area_stem',
    label: 'Área STEM',
    queryParam: 'area_stem',
    options: [
      { label: 'Ciencia', value: 'Ciencia' },
      { label: 'Tecnología', value: 'Tecnología' },
      { label: 'Ingeniería', value: 'Ingeniería' },
      { label: 'Matemáticas', value: 'Matemáticas' },
      { label: 'Robótica', value: 'Robótica' },
      { label: 'Inteligencia Artificial', value: 'Inteligencia Artificial' },
      { label: 'Medio Ambiente', value: 'Medio ambiente' },
      { label: 'Historia Natural', value: 'Historia Natural' },
      { label: 'Articulación y políticas públicas', value: 'Articulación y políticas públicas' },
    ],
  },
  {
    key: 'zona',
    label: 'Zona geográfica',
    queryParam: 'zona',
    options: [
      { label: 'Urbana', value: 'Urbana' },
      { label: 'Rural', value: 'Rural' },
      { label: 'Ambas', value: 'Ambas' },
    ],
  },
  {
    key: 'madurez',
    label: 'Madurez del programa',
    queryParam: 'madurez',
    options: [
      { label: 'Exploración', value: 'Exploración' },
      { label: 'Implementación', value: 'Implementación' },
      { label: 'Escalamiento', value: 'Escalamiento' },
    ],
  },
  {
    key: 'nivel_educativo',
    label: 'Nivel educativo',
    queryParam: 'nivel_educativo',
    options: [
      { label: 'Primaria', value: 'Primaria' },
      { label: 'Secundaria', value: 'Secundaria' },
      { label: 'Superior', value: 'Superior' },
      { label: 'Público general', value: 'Público general' },
    ],
  },
  {
    key: 'poblacion',
    label: 'Población objetivo',
    queryParam: 'poblacion',
    options: [
      { label: 'Niñez (6-12 años)', value: 'Niñez (6-12 años)' },
      { label: 'Adolescentes (13-17 años)', value: 'Adolescentes (13-17 años)' },
      { label: 'Jóvenes', value: 'Jóvenes' },
      { label: 'Profesionistas / Docentes / Emprendedores', value: 'Profesionistas / Docentes / Emprendedores' },
    ],
  },
  {
    key: 'pct_mujeres_rango',
    label: 'Participación femenina',
    queryParam: 'pct_mujeres_rango',
    options: [
      { label: '0% - 25%', value: '0-25' },
      { label: '26% - 50%', value: '26-50' },
      { label: '51% - 75%', value: '51-75' },
      { label: '76% - 100%', value: '76-100' },
    ],
  },
];

// Coordenadas de Ciudad Juárez
export const JUAREZ_CENTER: [number, number] = [31.7150, -106.4245];
export const DEFAULT_ZOOM = 13;
