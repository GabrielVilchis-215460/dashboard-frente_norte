// -- Tipos (TypeScript) --

export type OrganizationType =
  | 'centro_investigacion'
  | 'ong'
  | 'gobierno'
  | 'laboratorio'
  | 'institucion_educativa'
  | 'empresa_tecnologica'
  | 'makerspace'
  | 'centro_comunitario';

export type STEMArea =
  | 'ciencia'
  | 'tecnologia'
  | 'ingenieria'
  | 'matematicas'
  | 'robotica'
  | 'inteligencia_artificial';

export type MaturityLevel = 'exploracion' | 'implementacion' | 'escalamiento';

export type ActivityType =
  | 'taller'
  | 'curso'
  | 'bootcamp'
  | 'mentoria'
  | 'evento'
  | 'incubacion'
  | 'aceleracion';

export type EducationLevel =
  | 'primaria'
  | 'secundaria'
  | 'preparatoria'
  | 'universidad'
  | 'publico_general';

// Panorama General (Pestaña Overview) 

export interface TopOrganizacion {
  nombre: string;
  total_programas: number;
}

export interface PreviewMapaPoint {
  id: number;
  nombre: string;
  latitud: number;
  longitud: number;
  logo_url: string;
  total_programas: number;
}

export interface PanoramaGeneralResponse {
  total_organizaciones: number;
  total_programas_activos: number;
  beneficiarios_semestre: number;
  colonias_impactadas: number;
  pct_mujeres_beneficiarias: number;
  pct_programas_enfoque_integral: number;
  organizaciones_por_tipo: Record<string, number>;
  areas_stem_representadas: Record<string, number>;
  top_organizaciones: TopOrganizacion[];
  preview_mapa: PreviewMapaPoint[];
}

// --- Perfil de Beneficiarios ---

export interface BeneficiariosResponse {
  distribucion_etaria: Record<string, number>;
  distribucion_nivel_educativo: Record<EducationLevel, number>;
  distribucion_poblacion_objetivo: Record<string, number>;
  alcance_por_zona: Record<string, number>;
}

// Inclusión y Género 

export interface ProgramaFemenino {
  nombre: string;
  organizacion: string;
  porcentaje_femenino_range: string;
  descripcion: string;
}

export interface InclusionResponse {
  participacion_femenina_promedio: number;
  organizaciones_enfoque_mujeres: number;
  programas_ninas_adolescentes: number;
  distribucion_por_nivel: Record<EducationLevel, number>;
  programas_enfocados: ProgramaFemenino[];
}

// Oferta STEM

export interface OfertaSTEMResponse {
  programas_por_area: Record<STEMArea, number>;
  organizaciones_por_especialidad: Record<string, number>;
  tipos_actividad: Record<ActivityType, number>;
  heatmap_area_nivel: Record<STEMArea, Record<EducationLevel, number>>;
}

// Madurez del Ecosistema 

export interface MaturityStage {
  nivel: MaturityLevel;
  num_programas: number;
  beneficiarios: number;
  organizaciones: string[];
}

export interface MadurezResponse {
  etapas: MaturityStage[];
  organizaciones_por_nivel: Record<MaturityLevel, number>;
}

// Mapa del Ecosistema

export interface MapOrganizacion {
  id: number;
  nombre: string;
  tipo: OrganizationType;
  latitud: number;
  longitud: number;
  logo_url: string;
  areas_stem: STEMArea[];
  nivel_educativo: EducationLevel[];
  nivel_madurez: MaturityLevel;
  participacion_femenina: number;
  total_programas: number;
  zona: string;
  descripcion?: string;
}

export interface MapaEcosistemaResponse {
  organizaciones: MapOrganizacion[];
  total: number;
}

// UI

export interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export interface KPICard {
  label: string;
  value: string | number;
  icon: string;
  trend?: number;
}