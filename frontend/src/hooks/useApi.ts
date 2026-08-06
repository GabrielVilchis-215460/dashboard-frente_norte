import { useState, useEffect, useCallback, useRef } from 'react';
import type { ApiState } from '../types';

// Sin delay artificial — useMinDuration en cada componente controla el skeleton mínimo
const MIN_LOADING_MS = 0;
const CACHE_TTL = 5 * 60 * 1000; // 5 min

// Cache global en memoria — se limpia al recargar la página
const _cache = new Map<string, { data: unknown; ts: number }>();

function getCached<T>(key: string): T | null {
  const entry = _cache.get(key);
  if (entry && Date.now() - entry.ts < CACHE_TTL) return entry.data as T;
  return null;
}

export function useApi<T>(
  fetcher: () => Promise<T>,
  deps: unknown[] = []
): ApiState<T> & { refetch: () => void } {
  const key = fetcher.name; // e.g. "getBeneficiarios", "getPanoramaGeneral"
  const cached = key ? getCached<T>(key) : null;

  const [state, setState] = useState<ApiState<T>>({
    data: cached ?? null,
    loading: !cached,
    error: null,
  });

  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  const doFetch = useCallback(async (bust = false) => {
    if (!bust && key) {
      const hit = getCached<T>(key);
      if (hit) {
        setState({ data: hit, loading: false, error: null });
        return;
      }
    }

    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const [data] = await Promise.all([
        fetcherRef.current(),
        new Promise<void>((r) => setTimeout(r, MIN_LOADING_MS)),
      ]);
      if (key) _cache.set(key, { data, ts: Date.now() });
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({
        data: null,
        loading: false,
        error: err instanceof Error ? err.message : 'Error desconocido',
      });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps]);

  useEffect(() => {
    if (!cached) doFetch();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [doFetch]);

  // refetch siempre rompe el cache para ese endpoint
  const refetch = useCallback(() => {
    if (key) _cache.delete(key);
    doFetch(true);
  }, [doFetch, key]);

  return { ...state, refetch };
}

// Expuesto para limpiar el cache manualmente (e.g. después de un ETL)
export function invalidateApiCache(keyOrAll?: string) {
  if (!keyOrAll) _cache.clear();
  else _cache.delete(keyOrAll);
}
