// Utilidades de formato para etiquetas del backend

/** Formatea hora HH:MM:SS → HH:MM */
export function formatHora(hora?: string | null): string {
  if (!hora) return '';
  return hora.slice(0, 5);
}

/* Capitaliza y normaliza claves del backend para mostrarlas en UI */
export function formatLabel(raw: string): string {
  if (!raw) return raw;
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

/* Formatea un rango de fechas de evento */
export function formatFechaEvento(
  fecha: string,
  fecha_fin?: string | null
): string {
  const opts: Intl.DateTimeFormatOptions = {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    timeZone: 'UTC',
  };
  const d1 = new Date(fecha + 'T00:00:00Z');
  const s1 = d1.toLocaleDateString('es-MX', opts);
  if (!fecha_fin) return s1;
  const d2 = new Date(fecha_fin + 'T00:00:00Z');
  if (d1.toDateString() === d2.toDateString()) return s1;
  return `${s1} – ${d2.toLocaleDateString('es-MX', opts)}`;
}

/* Formatea un horario "HH:MM" o rango "HH:MM – HH:MM" */
export function formatHorario(
  hora_inicio: string,
  hora_fin?: string | null
): string {
  const trim = (h: string) => h.slice(0, 5);
  if (!hora_fin) return trim(hora_inicio);
  return `${trim(hora_inicio)} – ${trim(hora_fin)}`;
}