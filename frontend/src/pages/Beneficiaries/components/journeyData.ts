// Recorrido del beneficiario STEM: contenido estático

export interface JourneyStep {
  step: number;
  title: string;
  description: string;
  icon: string; // nombre del icono
}

export const JOURNEY_STEPS: JourneyStep[] = [
  {
    step: 1,
    title: 'Captación',
    description: 'Identificación y contacto inicial del beneficiario potencial',
    icon: 'IconUserSearch',
  },
  {
    step: 2,
    title: 'Diagnóstico',
    description: 'Evaluación de conocimientos y perfil para ubicar al participante',
    icon: 'IconClipboardCheck',
  },
  {
    step: 3,
    title: 'Formación',
    description: 'Participación activa en talleres, cursos y actividades STEM',
    icon: 'IconBooks',
  },
  {
    step: 4,
    title: 'Práctica',
    description: 'Aplicación de conocimientos en proyectos y retos reales',
    icon: 'IconTool',
  },
  {
    step: 5,
    title: 'Evaluación',
    description: 'Medición de impacto, competencias adquiridas y satisfacción',
    icon: 'IconChartBar',
  },
  {
    step: 6,
    title: 'Egreso',
    description: 'Graduación y seguimiento post-programa del participante',
    icon: 'IconCertificate',
  },
];