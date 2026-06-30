// Oferta STEM

import { DonutChart, HorizontalBarChart } from '../../components/charts';
import { Card } from '../../components/ui';
import { PageHeader } from '../../components/layout';
import { useApi } from '../../hooks/useApi';
import { api } from '../../services/api';
import { formatLabel } from '../../utils/format';
import { OrgCarousel } from './components/OrgCarousel';
import { ActivityCards } from './components/ActivityCards';
import styles from './STEMOffer.module.css';

export function STEMOffer() {
  const { data, loading, error, refetch } = useApi(api.getOfertaSTEM);

  // Barras de programas por área STEM
  const areaData = data?.programas_por_area
    ? Object.entries(data.programas_por_area).map(([name, value]) => ({
        name: formatLabel(name),
        value,
      }))
    : [];

  // Donut de modalidades
  const modalidadData = data?.modalidades_programas
    ? data.modalidades_programas.map((m) => ({
        name: formatLabel(m.name),
        value: m.value,
      }))
    : [];

  return (
    <div className={styles.page}>
      <PageHeader
        title="Oferta STEM"
        description="Programas, actividades y especialidades del ecosistema"
      />

      {error && (
        <div className={styles.errorBanner} role="alert">
          <span>No se pudieron cargar los datos: {error}</span>
          <button onClick={refetch} className={styles.retryBtn}>
            Reintentar
          </button>
        </div>
      )}

      {/* Fila superior: barras por área + carrusel de organizaciones */}
      <section className={`${styles.topGrid} stagger-children`}>
        <Card title="Programa por área de STEM" className={styles.areaCard}>
          <HorizontalBarChart data={areaData} loading={loading} fillHeight />
        </Card>

        <Card title="Organizaciones por especialidad" className={styles.orgCard}>
          <OrgCarousel
            orgs={data?.organizaciones_con_programas ?? []}
            loading={loading}
          />
        </Card>
      </section>

      {/* Fila inferior: donut modalidades + cards de actividades */}
      <section className={`${styles.bottomGrid} stagger-children`}>
        <Card title="Modalidades ofertadas" className={styles.modalidadCard}>
          <DonutChart data={modalidadData} loading={loading} />
        </Card>

        <Card title="Tipos de actividades" className={styles.actividadCard}>
          <ActivityCards
            actividades={data?.tipos_actividad_ofrecidos ?? {}}
            loading={loading}
          />
        </Card>
      </section>
    </div>
  );
}
