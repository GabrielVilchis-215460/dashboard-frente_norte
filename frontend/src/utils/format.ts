// Utilidades de formato para etiquetas del backend

/** Formatea fecha y rango de un evento para mostrar en UI */
export function formatFechaEvento(fecha: string, fechaFin?: string | null): string {
  const fmt = (d: string) =>
    new Date(d + 'T00:00:00').toLocaleDateString('es-MX', {
      day: 'numeric', month: 'long', year: 'numeric',
    });
  if (!fechaFin || fechaFin === fecha) return fmt(fecha);
  return `${fmt(fecha)} – ${fmt(fechaFin)}`;
}

/** Formatea hora HH:MM:SS → HH:MM */
export function formatHora(hora?: string | null): string {
  if (!hora) return '';
  return hora.slice(0, 5);
}

/** Rango horario como string legible */
export function formatHorario(horaInicio?: string | null, horaFin?: string | null): string {
  if (!horaInicio) return '';
  const ini = formatHora(horaInicio);
  return horaFin ? `${ini} – ${formatHora(horaFin)}` : ini;
}

/* Capitaliza y normaliza claves del backend para mostrarlas en UI. */
export function formatLabel(raw: string): string {
  if (!raw) return raw;

  // Si ya viene en mayúsculas lo respeta
  if (raw === raw.toUpperCase() && raw.length <= 5) return raw;

  return raw
    .replace(/_/g, ' ')
    .split(' ')
    .map((word) =>
      word.length > 0
        ? word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
        : word
    )
    .join(' ');
}