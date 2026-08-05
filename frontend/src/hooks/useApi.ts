// -- Hook para llamadas al backend --

import { useState, useEffect, useCallback } from 'react';
import type { ApiState } from '../types';

// Tiempo mínimo que el skeleton permanece visible antes de mostrar los datos.
// Evita el parpadeo cuando la API responde muy rápido y garantiza que la
// animación de entrada de las gráficas sea siempre perceptible.
const MIN_LOADING_MS = 500;

export function useApi<T>(
  fetcher: () => Promise<T>,
  deps: unknown[] = []
): ApiState<T> & { refetch: () => void } {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: true,
    error: null,
  });

  const fetch = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const [data] = await Promise.all([
        fetcher(),
        new Promise<void>((r) => setTimeout(r, MIN_LOADING_MS)),
      ]);
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({
        data: null,
        loading: false,
        error: err instanceof Error ? err.message : 'Error desconocido',
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { ...state, refetch: fetch };
}
