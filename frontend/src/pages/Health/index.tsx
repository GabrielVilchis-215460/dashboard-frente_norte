// Índice de Salud


import { Card } from '../../components/ui';
import { PageHeader } from '../../components/layout';
import { useApi } from '../../hooks/useApi';
import { api } from '../../services/api';
import { HealthFlask } from './components/HealthFlask';
import { DimensionBars } from './components/DimensionBars';
import { ISEFormulaTable } from './components/ISEFormulaTable';
import styles from './Health.module.css';
 
const ISE_DESCRIPTION =
  'El ISE (Índice de Salud del Ecosistema) mide la salud integral del ecosistema STEM en 5 dimensiones ponderadas con puntuación de 0 a 100.';
 
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
 
      {/* Fila superior: Nivel ISE (frasco) + Dimensiones */}
      <section className={`${styles.topGrid} stagger-children`}>
        <Card title="Nivel ISE" className={styles.flaskCard}>
          <div className={styles.flaskContent}>
            <HealthFlask
              score={data?.score_global ?? 0}
              nivel={data?.nivel ?? ''}
              loading={loading}
            />
            <p className={styles.iseDesc}>{ISE_DESCRIPTION}</p>
          </div>
        </Card>
 
        <Card title="Dimensiones del ISE" className={styles.dimCard}>
          <DimensionBars
            dimensiones={data?.dimensiones ?? []}
            loading={loading}
          />
        </Card>
      </section>
 
      {/* Fila inferior: Fórmula del ISE */}
      <Card title="Fórmula del ISE" className={styles.formulaCard}>
        <ISEFormulaTable
          dimensiones={data?.dimensiones ?? []}
          scoreGlobal={data?.score_global ?? 0}
          loading={loading}
        />
      </Card>
    </div>
  );
}
