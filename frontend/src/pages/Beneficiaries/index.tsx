// Beneficiaries — Perfil de Beneficiarios

import { DonutChart, HorizontalBarChart } from '../../components/charts';
import { Card } from '../../components/ui';
import { PageHeader } from '../../components/layout';
import { useApi } from '../../hooks/useApi';
import { api } from '../../services/api';
import { formatLabel } from '../../utils/format';
import { BeneficiaryJourney } from './components/BeneficiaryJourney';
import styles from './Beneficiaries.module.css';

export function Beneficiaries() {
  const { data, loading, error, refetch } = useApi(api.getBeneficiarios);

  const toChartData = (record?: Record<string, number>) =>
    record
      ? Object.entries(record).map(([name, value]) => ({
          name: formatLabel(name),
          value,
        }))
      : [];

  const grupoEtarioData = toChartData(data?.por_grupo_etario);
  const nivelEducativoData = toChartData(data?.por_nivel_educativo);
  const zonaData = toChartData(data?.por_zona);

  return (
    <div className={styles.page}>
      <PageHeader
        title="Perfil de Beneficiarios"
        description="Distribución demográfica de los beneficiarios del ecosistema STEM"
      />

      {error && (
        <div className={styles.errorBanner} role="alert">
          <span>No se pudieron cargar los datos: {error}</span>
          <button onClick={refetch} className={styles.retryBtn}>
            Reintentar
          </button>
        </div>
      )}

      {/* Fila superior: grupos de edad + nivel educativo */}
      <section className={`${styles.topGrid} stagger-children`}>
        <Card title="Programas por grupos de edad" className={styles.card}>
          <DonutChart data={grupoEtarioData} loading={loading} />
        </Card>

        <Card title="Programas por nivel educativo" className={styles.card}>
          <HorizontalBarChart data={nivelEducativoData} loading={loading} fillHeight/>
        </Card>
      </section>

      {/* Fila inferior: zona geográfica + recorrido */}
      <section className={`${styles.bottomGrid} stagger-children`}>
        <Card title="Programas por zona geográfica" className={styles.zonaCard}>
          <DonutChart data={zonaData} loading={loading} />
        </Card>

        <Card title="Recorrido del beneficiario STEM" className={styles.journeyCard}>
          <BeneficiaryJourney />
        </Card>
      </section>
    </div>
  );
}
