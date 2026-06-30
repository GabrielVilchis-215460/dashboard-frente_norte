// Overview — Panorama General

import {
  IconBuildingCommunity,
  IconTarget,
  IconMapPin,
  IconUsers,
  IconVenus,
  IconChartPie,
} from '@tabler/icons-react';
import {
  DonutChart,
  HorizontalBarChart,
} from '../../components/charts';
import { KPICard } from '../../components/dashboard';
import { Card } from '../../components/ui';
import { PageHeader } from '../../components/layout';
import { useApi } from '../../hooks/useApi';
import { api } from '../../services/api';
import { formatLabel } from '../../utils/format';
import { TopOrgTable } from './components/TopOrgTable';
import { MapPreview } from './components/MapPreview';
import styles from './Overview.module.css';

export function Overview() {
  const { data, loading, error, refetch } = useApi(api.getPanoramaGeneral);

  const kpis = [
    {
      label: 'Organizaciones STEM',
      value: data?.total_organizaciones ?? 0,
      icon: <IconBuildingCommunity size={28} stroke={1.2} />,
    },
    {
      label: 'Programas Activos',
      value: data?.total_programas_activos ?? 0,
      icon: <IconTarget size={28} stroke={1.2} />,
    },
    {
      label: 'Colonias impactadas',
      value: data?.colonias_impactadas ?? 0,
      icon: <IconMapPin size={28} stroke={1.2} />,
    },
    {
      label: 'Beneficiarios / Semestre',
      value: data?.beneficiarios_semestre
        ? data.beneficiarios_semestre.toLocaleString('es-MX')
        : 0,
      icon: <IconUsers size={28} stroke={1.2} />,
    },
    {
      label: 'Beneficiarias mujeres',
      value: data?.pct_mujeres_beneficiarias != null
        ? `${data.pct_mujeres_beneficiarias}%`
        : '—',
      icon: <IconVenus size={28} stroke={1.2} />,
    },
    {
      label: 'Programas enfoque integral',
      value: data?.pct_programas_enfoque_integral != null
        ? `${data.pct_programas_enfoque_integral}%`
        : '—',
      icon: <IconChartPie size={28} stroke={1.2} />,
    },
  ];

  // Preparar datos para la donut de organizaciones por tipo
  const donutData = data?.organizaciones_por_tipo
    ? Object.entries(data.organizaciones_por_tipo).map(([name, value]) => ({
        name: formatLabel(name),
        value,
      }))
    : [];

  // Preparar datos para la barra de áreas STEM
  const areasData = data?.areas_stem_representadas
    ? Object.entries(data.areas_stem_representadas).map(([name, value]) => ({
        name: formatLabel(name),
        value,
      }))
    : [];

  return (
    <div className={styles.page}>
      <PageHeader
        title="Panorama General"
        description="Vista general del estado del ecosistema STEM"
      />

      {error && (
        <div className={styles.errorBanner} role="alert">
          <span>No se pudieron cargar los datos: {error}</span>
          <button onClick={refetch} className={styles.retryBtn}>
            Reintentar
          </button>
        </div>
      )}

      {/* KPI Grid */}
      <section
        className={`${styles.kpiGrid} stagger-children`}
        aria-label="Indicadores clave"
      >
        {kpis.map((kpi, i) => (
          <KPICard
            key={kpi.label}
            label={kpi.label}
            value={kpi.value}
            icon={kpi.icon}
            loading={loading}
            animationDelay={i * 60}
          />
        ))}

        {/* Top organizaciones */}
        <div className={styles.topOrgCard}>
          <Card title="Top organizaciones por programas">
            <TopOrgTable
              items={data?.top_organizaciones ?? []}
              loading={loading}
            />
          </Card>
        </div>
      </section>

      {/* Donut + Barras + Mapa */}
      <section className={`${styles.bottomGrid} stagger-children`}>
        <Card title="Organizaciones por tipo" className={styles.donutCard}>
          <DonutChart data={donutData} loading={loading} />
        </Card>
 
        <Card title="Áreas" className={styles.barsCard}>
          <HorizontalBarChart data={areasData} loading={loading} />
        </Card>
 
        {/* Mapa */}
        <MapPreview points={data?.preview_mapa ?? []} loading={loading} className={styles.mapCard} />
      </section>
    </div>
  );
}
