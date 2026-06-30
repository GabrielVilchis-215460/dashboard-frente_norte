// Configuración de etapas de madurez
// Orden, colores, iconos y descripciones estáticas

export interface StageConfig {
  key: string;          // clave canónica para matchear con el backend
  label: string;        // nombre mostrado
  color: string;        // color de acento (icono, números) en bloques de detalle
  funnelColor: string;  // color del segmento en el embudo
  icon: string;         // nombre del icono de Tabler
  description: string;  // descripción estática
}

// Orden forzado
export const STAGES: StageConfig[] = [
  {
    key: 'exploracion',
    label: 'Exploración',
    color: '#689df3',
    funnelColor: '#3b82f6',
    icon: 'IconRocket',
    description:
      'Programas en fase de diseño o piloto. Están probando su modelo de impacto, definiendo la metodología y validando con grupos pequeños de beneficiarios.',
  },
  {
    key: 'implementacion',
    label: 'Implementación',
    color: '#44bec9',
    funnelColor: '#0e9aa8',
    icon: 'IconPlant',
    description:
      'Programas con ciclos completos de entrega. Cuentan con metodología probada, equipo estable y una base de beneficiarios constante semestre a semestre.',
  },
  {
    key: 'escalamiento',
    label: 'Escalamiento',
    color: '#2dd4bf',
    funnelColor: '#34d399',
    icon: 'IconTrendingUp',
    description:
      'Programas con impacto comprobado en proceso de crecimiento. Tienen alianzas estratégicas, financiamiento sostenido y buscan replicar su modelo a otras zonas.',
  },
];

/**
 * Normaliza una clave del backend (con acentos/mayúsculas) para matchear
 * con la config. Ej: "Exploración" → "exploracion"
 */
export function normalizeStage(raw: string): string {
  return raw
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, ''); // quita acentos
}

/** Busca la config de una etapa por su nombre del backend */
export function findStageConfig(backendKey: string): StageConfig | undefined {
  const norm = normalizeStage(backendKey);
  return STAGES.find((s) => s.key === norm);
}