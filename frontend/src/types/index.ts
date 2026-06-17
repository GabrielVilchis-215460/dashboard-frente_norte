// ── Tipos base que reflejan exactamente los schemas del backend ──

export interface Organizacion {
  id: number;
  nombre: string;
  tipo: string;
  areas_stem: string[];
  enfoque_principal?: string;
  descripcion?: string;
  logo_url?: string;
  contacto?: string;
  sitio_web?: string;
  latitud?: number;
  longitud?: number;
  direccion?: string;
  zona?: string;
  colonias: string[];
  activo: boolean;
  fuente?: string;
}

export interface OrganizacionMapPin {
  id: number;
  nombre: string;
  tipo: string;
  areas_stem: string[];
  latitud?: number;
  longitud?: number;
  zona?: string;
}

export interface Programa {
  id: number;
  organizacion_id: number;
  nombre: string;
  descripcion?: string;
  areas_stem: string[];
  tipos_actividad: string[];
  modalidad?: string;
  poblacion_objetivo?: string;
  nivel_educativo?: string;
  pct_mujeres_rango?: string;
  pct_mujeres_mid?: number;
  zona?: string;
  colonias_impacto: string[];
  volumen_semestral?: string;
  volumen_mid?: number;
  temporalidad?: string;
  madurez?: string;
  casos_exito?: string;
  siguiente_paso?: string;
  activo: boolean;
  fuente?: string;
}

// ── Tipos de métricas (módulos del dashboard) ──

export interface PanoramaGeneral {
  total_organizaciones: number;
  total_programas_activos: number;
  beneficiarios_semestre: number;
  colonias_impactadas: number;
  organizaciones_por_tipo: Record<string, number>;
  areas_stem_representadas: string[];
}

export interface PerfilBeneficiarios {
  por_grupo_etario: Record<string, number>;
  por_nivel_educativo: Record<string, number>;
  por_zona: Record<string, number>;
}

export interface InclusionFemenina {
  pct_promedio_mujeres: number;
  programas_enfocados_mujeres: number;
  programas_ninas_adolescentes: number;
  por_nivel_educativo: Record<string, number>;
}

export interface OfertaSTEM {
  programas_por_area: Record<string, number>;
  tipos_actividad_ofrecidos: Record<string, number>;
  organizaciones_por_especialidad: Record<string, number>;
}

export interface MadurezEcosistema {
  por_etapa: Record<string, number>;
  beneficiarios_por_etapa: Record<string, number>;
  organizaciones_por_madurez: Record<string, number>;
}

export interface CoberturaColonia {
  nombre: string;
  zona?: string;
  latitud?: number;
  longitud?: number;
  num_programas: number;
  nivel_oferta: string;
}

export interface CoberturaTerritorial {
  total_colonias_impactadas: number;
  por_zona: Record<string, number>;
  colonias_detalle: CoberturaColonia[];
  zonas_baja_oferta: string[];
}

export interface DimensionISE {
  nombre: string;
  score: number;
  peso: number;
  descripcion: string;
}

export interface IndiceSaludEcosistema {
  score_global: number;
  nivel: string;
  dimensiones: DimensionISE[];
}

// ── Tipos de UI ──

export type ModuloDashboard =
  | 'panorama'
  | 'beneficiarios'
  | 'inclusion'
  | 'oferta'
  | 'madurez'
  | 'cobertura'
  | 'mapa'
  | 'indice';
