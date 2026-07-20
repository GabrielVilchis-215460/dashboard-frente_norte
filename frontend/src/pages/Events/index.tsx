import { Card } from '../../components/ui';
import { KPICard } from '../../components/dashboard';
import { DonutChart } from '../../components/charts';
import { PageHeader } from '../../components/layout';
import { useApi } from '../../hooks/useApi';
import { api } from '../../services/api';
import { EventCarousel } from './components/EventCarousel';
import { EventsAreaChart } from './components/EventsAreaChart';
import styles from './Events.module.css';

export function Events() {
  const { data: metricas, loading: loadingM } = useApi(api.getEventosMetricas);
  const { data: proximos, loading: loadingP } = useApi(api.getEventosProximos);

  const historico = metricas?.historico_eventos_trimestral ?? [];
  const delta = historico.length >= 2   // diferencia entre último y penúltimo trimestre
    ? historico[historico.length - 1].eventos - historico[historico.length - 2].eventos
    : null;
  const eventosTrimestre = historico.length
    ? historico[historico.length - 1].eventos
    : 0;

  // Donut tipo
  const tipoData = (metricas?.distribucion_eventos_tipo ?? []).map((d) => ({
    name: d.label,
    value: d.count,
  }));

  // Donut enfoque
  const enfoqueData = (metricas?.distribucion_eventos_enfoque ?? []).map((d) => ({
    name: d.label,
    value: d.count,
  }));

  return (
    <div className={styles.page}>
      <PageHeader
        title="Eventos"
        description="Todos los eventos realizados por las organizaciones que conforman el ecosistema STEM"
      />

      {/* Fila 1: 2 KPIs + 2 Donuts */}
      <section className={`${styles.topGrid} stagger-children`}>
        <div className={styles.kpiColumn}>
          <KPICard
            label="Eventos este trimestre"
            value={loadingM ? '—' : eventosTrimestre}
            loading={loadingM}
            badge={
              delta !== null && !loadingM
                ? { value: delta, positive: delta >= 0 }
                : undefined
            }
          />
          <KPICard
            label="Organizaciones con eventos activos"
            value={loadingM ? '—' : (metricas?.organizaciones_con_eventos_activos ?? 0)}
            loading={loadingM}
          />
        </div>

        {/* Donut tipo */}
        <Card title="Porcentaje de eventos por tipo" className={styles.donutCard}>
          <DonutChart data={tipoData} loading={loadingM} />
        </Card>

        {/* Donut enfoque */}
        <Card title="Porcentaje de eventos por enfoque" className={styles.donutCard}>
          <DonutChart data={enfoqueData} loading={loadingM} />
        </Card>
      </section>

      {/* Fila 2: Gráfica histórico + Carrusel */}
      <section className={`${styles.bottomGrid} stagger-children`}>
        <Card title="Eventos por trimestre" className={styles.chartCard}>
          <EventsAreaChart
            data={historico}
            loading={loadingM}
          />
        </Card>

        <Card title="Eventos próximos" className={styles.carouselCard}>
          <EventCarousel
            eventos={proximos ?? []}
            loading={loadingP}
          />
        </Card>
      </section>
    </div>
  );
}