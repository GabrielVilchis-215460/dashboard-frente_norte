// Inclusion — Inclusión y Género

import { CenterDonut, HorizontalBarChart } from '../../components/charts';
import { KPICard } from '../../components/dashboard';
import { Card } from '../../components/ui';
import { PageHeader } from '../../components/layout';
import { useApi } from '../../hooks/useApi';
import { api } from '../../services/api';
import { formatLabel } from '../../utils/format';
import { ProgramCarousel } from './components/ProgramCarousel';
import styles from './Inclusion.module.css';
 
export function Inclusion() {
  const { data, loading, error, refetch } = useApi(api.getInclusion);
 
  // Barras de distribución por rango de participación
  const rangoData = data?.distribucion_por_rango
    ? data.distribucion_por_rango.map((r) => ({
        name: r.rango,
        value: r.cantidad,
      }))
    : [];
 
  // Barras por nivel educativo
  const nivelData = data?.por_nivel_educativo
    ? Object.entries(data.por_nivel_educativo).map(([name, value]) => ({
        name: formatLabel(name),
        value,
      }))
    : [];
 
  return (
    <div className={styles.page}>
      <PageHeader
        title="Inclusión y Género"
        description="Participación femenina y programas dirigidos a mujeres y niñas"
      />
 
      {error && (
        <div className={styles.errorBanner} role="alert">
          <span>No se pudieron cargar los datos: {error}</span>
          <button onClick={refetch} className={styles.retryBtn}>
            Reintentar
          </button>
        </div>
      )}
 
      {/* Fila superior: donut central + 2 KPI + barras de rangos */}
      <section className={`${styles.topGrid} stagger-children`}>
        <Card title="Porcentaje de inclusión femenina global" className={styles.donutCard}>
          <CenterDonut
            value={data?.pct_promedio_mujeres ?? 0}
            loading={loading}
          />
        </Card>
 
        <div className={styles.kpiColumn}>
          <KPICard
            label="Programas enfocados en mujeres"
            value={data?.total_enfocados_mujeres ?? 0}
            loading={loading}
          />
          <KPICard
            label="Programas para niñas y adolescentes"
            value={data?.total_ninas_adolescentes ?? 0}
            loading={loading}
          />
        </div>
 
        <Card title="Porcentaje de beneficiarios mujeres por programa" className={styles.rangoCard}>
          <HorizontalBarChart data={rangoData} loading={loading} fillHeight />
        </Card>
      </section>
 
      {/* Fila inferior: barras por nivel + carrusel */}
      <section className={`${styles.bottomGrid} stagger-children`}>
        <Card title="Participación femenina por nivel educativo" className={styles.nivelCard}>
          <HorizontalBarChart data={nivelData} loading={loading} fillHeight />
        </Card>
 
        <Card title="Programas enfocados en mujeres y niñas" className={styles.carouselCard}>
          <ProgramCarousel
            programas={data?.carrusel_programas_destacados ?? []}
            loading={loading}
          />
        </Card>
      </section>
    </div>
  );
}
