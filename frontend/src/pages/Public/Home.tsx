import { useEffect, useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { IconSearch, IconArrowRight } from '@tabler/icons-react';
import { CategoryIcons } from '../../components/public/CategoryIcons';
import { EventGridCard } from '../../components/public/EventGridCard';
import { PublicMap } from '../../components/public/PublicMap';
import { Skeleton } from '../../components/ui';
import { publicApi } from '../../services/publicApi';
import { ROUTES } from '../../constants/routes';
import type { Evento, EventoMapPoint } from '../../types';
import styles from './Home.module.css';

export function Home() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');

  const [destacados, setDestacados] = useState<Evento[] | null>(null);
  const [eventPoints, setEventPoints] = useState<EventoMapPoint[]>([]);
  const [loadingDestacados, setLoadingDestacados] = useState(true);
  const [loadingMapa, setLoadingMapa] = useState(true);

  useEffect(() => {
    publicApi.getEventosDestacados(8)
      .then(setDestacados)
      .catch(() => setDestacados([]))
      .finally(() => setLoadingDestacados(false));

    publicApi.getEventosMapa()
      .then(setEventPoints)
      .catch(() => setEventPoints([]))
      .finally(() => setLoadingMapa(false));
  }, []);

  function handleSearch(e: FormEvent) {
    e.preventDefault();
    const params = query.trim() ? `?q=${encodeURIComponent(query.trim())}` : '';
    navigate(`${ROUTES.EVENTS}${params}`);
  }

  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <h1 className={styles.heroTitle}>ECOSISTEMA STEM</h1>
        <p className={styles.heroSubtitle}>
          Explora los eventos más relevantes sobre ciencia, tecnología, ingeniería
          y matemáticas en Ciudad Juárez
        </p>

        <form className={styles.searchForm} onSubmit={handleSearch}>
          <input
            type="text"
            className={styles.searchInput}
            placeholder="Ingresa tu búsqueda"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit" className={styles.searchBtn} aria-label="Buscar">
            <IconSearch size={18} stroke={1.8} />
          </button>
        </form>
      </section>

      <CategoryIcons />

      <section className={styles.section}>
        <h2 className={styles.sectionTitle} id="mapa">Mapa</h2>
        {loadingMapa ? (
          <Skeleton width="100%" height="380px" borderRadius="16px" />
        ) : (
          <PublicMap eventPoints={eventPoints} />
        )}
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Eventos</h2>
          <button
            type="button"
            className={styles.verTodos}
            onClick={() => navigate(ROUTES.EVENTS)}
          >
            Ver todos <IconArrowRight size={16} stroke={1.8} />
          </button>
        </div>

        <div className={styles.grid}>
          {loadingDestacados
            ? Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} height="280px" borderRadius="16px" />
              ))
            : destacados?.map((ev) => <EventGridCard key={ev.id} evento={ev} />)}
        </div>

        {!loadingDestacados && destacados?.length === 0 && (
          <p className={styles.empty}>No hay eventos próximos por ahora.</p>
        )}
      </section>
    </div>
  );
}