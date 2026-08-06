import { useState, useEffect, useRef } from 'react';

/**
 * Garantiza que `loading` sea true durante al menos `minMs` milisegundos.
 * Evita el flash de skeleton de <50ms cuando la API responde muy rápido —
 * en esos casos lo que se ve es peor que no mostrar nada.
 * Si la petición tarda más de `minMs`, no añade ningún delay extra.
 */
export function useMinDuration(loading: boolean, minMs = 400): boolean {
  const [visible, setVisible] = useState(loading);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const startRef = useRef<number>(loading ? Date.now() : 0);

  useEffect(() => {
    if (loading) {
      startRef.current = Date.now();
      setVisible(true);
      return;
    }

    const elapsed = Date.now() - startRef.current;
    const remaining = minMs - elapsed;

    if (remaining <= 0) {
      setVisible(false);
    } else {
      timerRef.current = setTimeout(() => setVisible(false), remaining);
    }

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [loading, minMs]);

  return visible;
}
