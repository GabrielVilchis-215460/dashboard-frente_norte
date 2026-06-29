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
  por_grupo_etario: Record<string, number>;
  por_nivel_educativo: Record<string, number>;
  por_zona: Record<string, number>;
}

// Inclusión y Género 

export interface RangoParticipacion {
  rango: string;
  cantidad: number;
}
 
export interface ProgramaDetalle {
  nombre: string;
  organizacion: string;
  pct_mujeres: number;
  descripcion: string | null;
}
 
export interface InclusionResponse {
  pct_promedio_mujeres: number;
  total_ninas_adolescentes: number;
  total_enfocados_mujeres: number;
  distribucion_por_rango: RangoParticipacion[];
  por_nivel_educativo: Record<string, number>;
  carrusel_programas_destacados: ProgramaDetalle[];
}

// Oferta STEM

export interface ModalidadPrograma {
  name: string;
  value: number;
}

export interface OrganizacionProgramas {
  logo_url: string | null;
  organizacion: string;
  enfoque_principal: string | null;
  tipo_organizacion: string | null;
  programas: string[];
}

export interface OfertaSTEMResponse {
  programas_por_area: Record<string, number>;
  tipos_actividad_ofrecidos: Record<string, number>;
  organizaciones_con_programas: OrganizacionProgramas[];
  modalidades_programas: ModalidadPrograma[];
}

// Madurez del Ecosistema 
export interface MadurezDetalle {
  etapa: string;
  cantidad: number;
  organizaciones: string[];
}
 
export interface MadurezResponse {
  por_etapa: Record<string, number>;
  beneficiarios_por_etapa: Record<string, number>;
  organizaciones_por_madurez: MadurezDetalle[];
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

// Índice de Salud del Ecosistema (ISE) 
 
export interface DimensionISE {
  nombre: string;
  score: number;
  peso: number;
  descripcion: string;
}
 
export interface IndiceSaludResponse {
  score_global: number;
  nivel: string;
  dimensiones: DimensionISE[];
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