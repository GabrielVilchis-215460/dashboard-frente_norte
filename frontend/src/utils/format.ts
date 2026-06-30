// Utilidades de formato para etiquetas del backend

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