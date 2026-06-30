// Tabla de la fórmula del ISE

import { Skeleton } from '../../../components/ui';
import type { DimensionISE } from '../../../types';
import styles from './ISEFormulaTable.module.css';

interface Props {
  dimensiones: DimensionISE[];
  scoreGlobal: number;
  loading: boolean;
}

// Color por dimensión
const DIM_COLORS = ['#34d3ab', '#34c8d3', '#60bcfa', '#59a4fa', '#7086ff'];

export function ISEFormulaTable({ dimensiones, scoreGlobal, loading }: Props) {
  if (loading) {
    return (
      <div className={styles.skeletonWrap}>
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} width="100%" height="32px" />
        ))}
      </div>
    );
  }

  if (!dimensiones.length) {
    return <p className={styles.empty}>Sin datos disponibles</p>;
  }

  return (
    <div className={styles.tableWrap}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th className={styles.thLeft}>Dimensión</th>
            <th>Peso</th>
            <th>Score</th>
            <th>Contribución</th>
            <th className={styles.thLeft}>Descripción</th>
          </tr>
        </thead>
        <tbody>
          {dimensiones.map((dim, i) => {
            const contribucion = dim.score * dim.peso;
            const color = DIM_COLORS[i % DIM_COLORS.length];
            return (
              <tr key={dim.nombre} className={styles.row}>
                <td className={styles.dimName} style={{ color }}>
                  {dim.nombre}
                </td>
                <td className={styles.center}>{Math.round(dim.peso * 100)}%</td>
                <td className={`${styles.center} ${styles.bold}`}>
                  {dim.score.toFixed(1).replace(/\.0$/, '')}
                </td>
                <td className={styles.center} style={{ color, fontWeight: 600 }}>
                  {contribucion.toFixed(1)}
                </td>
                <td className={styles.desc}>{dim.descripcion}</td>
              </tr>
            );
          })}

          {/* Fila de total */}
          <tr className={styles.totalRow}>
            <td className={styles.bold}>Score global</td>
            <td></td>
            <td></td>
            <td className={`${styles.center} ${styles.totalValue}`}>
              {scoreGlobal.toFixed(1)}
            </td>
            <td className={styles.desc}>Suma de las 5 contribuciones ponderadas</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}