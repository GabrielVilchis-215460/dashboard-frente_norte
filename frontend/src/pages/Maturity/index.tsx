// Madurez del Ecosistema

import { Card } from '../../components/ui';
import { PageHeader } from '../../components/layout';
import { useApi } from '../../hooks/useApi';
import { api } from '../../services/api';
import { MaturityFunnel } from './components/MaturityFunnel';
import { OrgsByStage } from './components/OrgsByStage';
import styles from './Maturity.module.css';

export function Maturity() {
  const { data, loading, error, refetch } = useApi(api.getMadurez);

  return (
    <div className={styles.page}>
      <PageHeader
        title="Madurez del Ecosistema"
        description="Clasificación de programas y organizaciones por etapa de desarrollo"
      />

      {error && (
        <div className={styles.errorBanner} role="alert">
          <span>No se pudieron cargar los datos: {error}</span>
          <button onClick={refetch} className={styles.retryBtn}>
            Reintentar
          </button>
        </div>
      )}

      {/* Niveles de madurez: funnel + detalle */}
      <Card title="Niveles de madurez" className={styles.funnelCard}>
        <MaturityFunnel data={data ?? undefined} loading={loading} />
      </Card>

      {/* Organizaciones por nivel de madurez */}
      <Card title="Organizaciones por nivel de madurez" className={styles.orgsCard}>
        <OrgsByStage
          detalles={data?.organizaciones_por_madurez ?? []}
          loading={loading}
        />
      </Card>
    </div>
  );
}
