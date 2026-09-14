// Índice de Salud


import { Card } from '../../components/ui';
import { PageHeader } from '../../components/layout';
import { useApi } from '../../hooks/useApi';
import { api } from '../../services/api';
import { KPICards } from './components/KPICards';
import { EvolutionCarousel } from './components/EvolutionCarousel';
import { BenchmarkCarousel } from './components/BenchmarkCarousel';
import { InfoTooltip } from './components/InfoTooltip';
import styles from './Health.module.css';

export function Health() {
  const { data, loading, error, refetch } = useApi(api.getIndiceSalud);

  return (
    <div className={styles.page}>
      <PageHeader
        title="Índice de Salud"
        description="Indicador compuesto del ecosistema STEM de Ciudad Juárez"
      />

      {error && (
        <div className={styles.errorBanner} role="alert">
          <span>No se pudieron cargar los datos: {error}</span>
          <button onClick={refetch} className={styles.retryBtn}>
            Reintentar
          </button>
        </div>
      )}

      {/* Estado actual (KPIs)*/}
      <Card
        title="Estado actual del ecosistema STEM"
        action={<InfoTooltip text='Indicadores clave del ecosistema STEM de Ciudad Juárez.'/>}
        className={styles.kpiCard}
      >
        <KPICards kpis={data?.kpis ?? []} loading={loading} />
      </Card>

      {/* Evolución + Benchmark */}
      <section className={`${styles.bottomGrid} stagger-children`}>
        <Card
          title="Evolución de Ciudad Juárez"
          action={<InfoTooltip text='Tendencias de los principales indicadores a través de los años.'/>}
          className={styles.chartCard}
        >
          <EvolutionCarousel slides={data?.carrusel_evolucion ?? []} loading={loading} />
        </Card>

        <Card
          title="Benchmark"
          action={<InfoTooltip text='Comparación con ecosistemas referentes.'/>}
          className={styles.chartCard}
        >
          <BenchmarkCarousel slides={data?.carrusel_benchmark ?? []} loading={loading} />
        </Card>
      </section>
    </div>
  );
}
