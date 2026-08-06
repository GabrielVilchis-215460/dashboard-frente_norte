import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { IconSearch, IconFilter, IconArrowLeft, IconX } from '@tabler/icons-react';
import { EventGridCard } from '../../components/public/EventGridCard';
import { Skeleton } from '../../components/ui';
import { publicApi } from '../../services/publicApi';
import { ROUTES } from '../../constants/routes';
import type { Evento } from '../../types';
import styles from './EventList.module.css';

const TIPOS = ['Talleres', 'Cursos', 'Bootcamp', 'Campamento', 'Eventos', 'Conferencias'];
const ENFOQUES = [
  'Ciencia', 'Tecnologia', 'Ingenieria', 'Matematicas', 'Robotica',
  'Inteligencia artificial', 'Medio ambiente', 'Finanzas', 'Emprendimiento',
];

export function EventList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [items, setItems] = useState<Evento[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  // staleItems mantiene los resultados anteriores visibles mientras cargan los nuevos
  const [staleItems, setStaleItems] = useState<Evento[]>([]);
  const [filtrosAbiertos, setFiltrosAbiertos] = useState(false);

  const q = searchParams.get('q') ?? '';
  const tipo = searchParams.get('tipo') ?? '';
  const enfoque = searchParams.get('enfoque') ?? '';
  const orden = (searchParams.get('orden') as 'recientes' | 'populares') ?? 'recientes';

  const [queryInput, setQueryInput] = useState(q);

  const hayFiltrosActivos = Boolean(tipo || enfoque || orden === 'populares');

  useEffect(() => {
    // Guarda los items actuales como stale antes de empezar a cargar
    setStaleItems((prev) => (items.length > 0 ? items : prev));
    setLoading(true);
    publicApi
      .getEventosPublico({
        q: q || undefined,
        tipo: tipo || undefined,
        enfoque: enfoque || undefined,
        orden,
        limit: 24,
      })
      .then((res) => {
        setItems(res.items);
        setTotal(res.total);
        setStaleItems([]);
      })
      .catch(() => {
        setItems([]);
        setTotal(0);
        setStaleItems([]);
      })
      .finally(() => setLoading(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q, tipo, enfoque, orden]);

  function updateParam(key: string, value: string) {
    const next = new URLSearchParams(searchParams);
    if (value) next.set(key, value);
    else next.delete(key);
    setSearchParams(next);
  }

  function handleSearchSubmit(e: React.FormEvent) {
    e.preventDefault();
    updateParam('q', queryInput.trim());
  }

  function limpiarFiltros() {
    const next = new URLSearchParams(searchParams);
    next.delete('tipo');
    next.delete('enfoque');
    next.delete('orden');
    setSearchParams(next);
  }

  function limpiarTodo() {
    setQueryInput('');
    setSearchParams(new URLSearchParams());
  }

  const titulo = q
    ? `Resultados para "${q}"`
    : orden === 'populares'
      ? 'Eventos populares'
      : 'Todos los eventos';

  return (
    <div className={styles.page}>
      <Link to={ROUTES.HOME} className={styles.backLink}>
        <IconArrowLeft size={16} stroke={1.8} /> Volver a inicio
      </Link>

      <div className={styles.header}>
        <h1 className={styles.title}>{titulo}</h1>

        <div className={styles.controls}>
          <form className={styles.searchForm} onSubmit={handleSearchSubmit}>
            <IconSearch size={16} stroke={1.8} className={styles.searchIcon} />
            <input
              className={styles.searchInput}
              placeholder="Buscar..."
              value={queryInput}
              onChange={(e) => setQueryInput(e.target.value)}
            />
          </form>

          <div className={styles.filterWrap}>
            <button
              type="button"
              className={styles.filterBtn}
              onClick={() => setFiltrosAbiertos((v) => !v)}
            >
              <IconFilter size={16} stroke={1.8} />
              Filtrar
            </button>

            {filtrosAbiertos && (
              <div className={styles.filterPanel}>
                <label className={styles.filterLabel}>
                  Orden
                  <select
                    className={styles.filterSelect}
                    value={orden}
                    onChange={(e) => updateParam('orden', e.target.value)}
                  >
                    <option value="recientes">Fecha</option>
                    <option value="populares">Popular</option>
                  </select>
                </label>

                <label className={styles.filterLabel}>
                  Tipo
                  <select
                    className={styles.filterSelect}
                    value={tipo}
                    onChange={(e) => updateParam('tipo', e.target.value)}
                  >
                    <option value="">Todos</option>
                    {TIPOS.map((t) => <option key={t} value={t}>{t}</option>)}
                  </select>
                </label>

                <label className={styles.filterLabel}>
                  Enfoque
                  <select
                    className={styles.filterSelect}
                    value={enfoque}
                    onChange={(e) => updateParam('enfoque', e.target.value)}
                  >
                    <option value="">Todos</option>
                    {ENFOQUES.map((f) => <option key={f} value={f}>{f}</option>)}
                  </select>
                </label>

                { hayFiltrosActivos && <button
                  type="button"
                  className={styles.clearFiltersBtn}
                  onClick={limpiarFiltros}
                  disabled={!hayFiltrosActivos}
                >
                  <IconX size={14} stroke={1.8} />
                  Limpiar filtros
                </button>}
              </div>
            )}
          </div>
        </div>
      </div>

      <p className={styles.counter}>
        {loading ? 'Buscando...' : `${total} evento${total === 1 ? '' : 's'} encontrado${total === 1 ? '' : 's'}`}
      </p>

      <div
        className={styles.grid}
        style={loading && staleItems.length > 0 ? { opacity: 0.5, transition: 'opacity 0.2s ease', pointerEvents: 'none' } : undefined}
      >
        {loading && staleItems.length === 0
          ? Array.from({ length: 8 }).map((_, i) => (
              <Skeleton key={i} height="280px" borderRadius="16px" />
            ))
          : (loading ? staleItems : items).map((ev) => <EventGridCard key={ev.id} evento={ev} />)}
      </div>

      {!loading && items.length === 0 && (
        <div className={styles.emptyState}>
          <p className={styles.empty}>No se encontraron eventos con esos filtros.</p>
          <button type="button" className={styles.emptyCta} onClick={limpiarTodo}>
            Ver todos los eventos
          </button>
        </div>
      )}
    </div>
  );
}