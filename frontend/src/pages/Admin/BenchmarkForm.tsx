import { useEffect, useRef, useState } from 'react';
import { IconX, IconRotate } from '@tabler/icons-react';
import { adminApi } from '../../services/adminApi';
import type { Indicador } from '../../services/adminApi';
import { ConfirmDialog } from '../../components/common/ConfirmDialog';
import formStyles from './AdminForm.module.css';
import styles from './BenchmarkForm.module.css';

export interface PendingDelete {
  indicadorId: number;
  benchmarkId: number;
}

interface Props {
  ecosistemaId: number;
  indicadores: Indicador[];
  /** Se llama con cada cambio: el padre guarda esto y lo usa al confirmar
   *  Primero ejecuta los pendingDeletes, luego el upsert de valores
   *  Nada se borra hasta que el padre llama a guardar. */
  onChange: (anio: number, valores: Record<number, string>, pendingDeletes: PendingDelete[]) => void;
}

const ANIO_ACTUAL = new Date().getFullYear();
const ANIOS_DISPONIBLES = Array.from({ length: 10 }, (_, i) => ANIO_ACTUAL - 8 + i);

export function BenchmarkForm({ ecosistemaId, indicadores, onChange }: Props) {
  const [anio, setAnio] = useState(ANIO_ACTUAL);
  const [valores, setValores] = useState<Record<number, string>>({});
  const [idsExistentes, setIdsExistentes] = useState<Record<number, number>>({});
  const [pendingDeletes, setPendingDeletes] = useState<Record<number, number>>({}); // indicadorId -> benchmarkId
  const [loading, setLoading] = useState(false);

  const snapshotRef = useRef<string>('{}'); // último estado cargado o recién guardado

  const [confirmarCambioAnio, setConfirmarCambioAnio] = useState<number | null>(null); // año destino pendiente de confirmar

  function cargarAnio(nuevoAnio: number) {
    setLoading(true);
    adminApi
      .getBenchmarksEcosistema(ecosistemaId, nuevoAnio)
      .then((registros) => {
        const nuevosValores: Record<number, string> = {};
        const nuevosIds: Record<number, number> = {};
        registros.forEach((r) => {
          nuevosValores[r.indicador_id] = String(r.valor);
          nuevosIds[r.indicador_id] = r.id;
        });
        setValores(nuevosValores);
        setIdsExistentes(nuevosIds);
        setPendingDeletes({});
        snapshotRef.current = JSON.stringify(nuevosValores);
        onChange(nuevoAnio, nuevosValores, []);
      })
      .catch(() => {
        setValores({});
        setIdsExistentes({});
        setPendingDeletes({});
        snapshotRef.current = '{}';
        onChange(nuevoAnio, {}, []);
      })
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    cargarAnio(anio);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ecosistemaId]);

  function hayPendientes(): boolean {
    return JSON.stringify(valores) !== snapshotRef.current || Object.keys(pendingDeletes).length > 0;
  }

  function handleAnioChange(nuevoAnioStr: string) {
    const nuevoAnio = parseInt(nuevoAnioStr);
    if (hayPendientes()) {
      setConfirmarCambioAnio(nuevoAnio); // abre el ConfirmDialog; el <select> revierte solo (controlado)
      return;
    }
    setAnio(nuevoAnio);
    cargarAnio(nuevoAnio);
  }

  function confirmarDescartarYCambiar() {
    if (confirmarCambioAnio === null) return;
    const nuevoAnio = confirmarCambioAnio;
    setConfirmarCambioAnio(null);
    setAnio(nuevoAnio);
    cargarAnio(nuevoAnio);
  }

  function emitirCambio(nuevosValores: Record<number, string>, nuevosPendientes: Record<number, number>) {
    const lista: PendingDelete[] = Object.entries(nuevosPendientes).map(([indId, benchId]) => ({
      indicadorId: Number(indId),
      benchmarkId: benchId,
    }));
    onChange(anio, nuevosValores, lista);
  }

  function setValor(indicadorId: number, val: string) {
    const nuevos = { ...valores, [indicadorId]: val };
    setValores(nuevos);
    emitirCambio(nuevos, pendingDeletes);
  }

  // Marcar/desmarcar para borrar queda
  // "en espera" hasta que se confirme el guardado del modal completo.
  function marcarParaEliminar(indicadorId: number) {
    const benchmarkId = idsExistentes[indicadorId];
    if (!benchmarkId) return;
    const nuevosPendientes = { ...pendingDeletes, [indicadorId]: benchmarkId };
    setPendingDeletes(nuevosPendientes);
    emitirCambio(valores, nuevosPendientes);
  }

  function deshacerEliminar(indicadorId: number) {
    const nuevosPendientes = { ...pendingDeletes };
    delete nuevosPendientes[indicadorId];
    setPendingDeletes(nuevosPendientes);
    emitirCambio(valores, nuevosPendientes);
  }

  return (
    <div className={formStyles.grid}>
      <div className={formStyles.fieldGroup}>
        <label className={formStyles.label}>Año</label>
        <select
          className={formStyles.select}
          value={anio}
          onChange={(e) => handleAnioChange(e.target.value)}
        >
          {ANIOS_DISPONIBLES.map((a) => <option key={a} value={a}>{a}</option>)}
        </select>
      </div>

      <span className={formStyles.sectionTitle}>
        Valores {loading && '— cargando...'}
      </span>

      {indicadores.map((ind) => {
        const marcadoParaBorrar = pendingDeletes[ind.id] !== undefined;
        return (
          <div key={ind.id} className={formStyles.fieldGroup}>
            <label className={formStyles.label}>{ind.nombre} ({ind.unidad})</label>
            <div className={styles.inputRow}>
              <input
                className={`${formStyles.input} ${styles.numberInput} ${marcadoParaBorrar ? styles.inputMarked : ''}`}
                type="number"
                step="any"
                value={valores[ind.id] ?? ''}
                onChange={(e) => setValor(ind.id, e.target.value)}
                placeholder="Sin dato"
                disabled={marcadoParaBorrar}
              />
              {idsExistentes[ind.id] !== undefined && !marcadoParaBorrar && (
                <button
                  type="button"
                  className={styles.clearBtn}
                  onClick={() => marcarParaEliminar(ind.id)}
                  aria-label={`Eliminar valor de ${ind.nombre}`}
                  title="Eliminar este valor (se aplica al guardar)"
                >
                  <IconX size={14} stroke={2} />
                </button>
              )}
              {marcadoParaBorrar && (
                <button
                  type="button"
                  className={styles.undoBtn}
                  onClick={() => deshacerEliminar(ind.id)}
                  aria-label={`Deshacer eliminación de ${ind.nombre}`}
                  title="Deshacer"
                >
                  <IconRotate size={14} stroke={2} />
                </button>
              )}
            </div>
            {marcadoParaBorrar && (
              <span className={styles.markedNote}>Se eliminará al guardar</span>
            )}
          </div>
        );
      })}

      {confirmarCambioAnio !== null && (
        <ConfirmDialog
          title="¿Cambiar de año?"
          message={`Tienes cambios sin guardar en ${anio}. Si cambias de año se van a perder. ¿Quieres continuar?`}
          confirmLabel="Cambiar de año"
          cancelLabel="Cancelar"
          danger
          onConfirm={confirmarDescartarYCambiar}
          onCancel={() => setConfirmarCambioAnio(null)}
        />
      )}
    </div>
  );
}