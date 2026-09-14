import { useState, useMemo } from 'react';
import { Skeleton } from '../../components/ui';
import { useApi } from '../../hooks/useApi';
import { adminApi } from '../../services/adminApi';
import type { Ecosistema } from '../../services/adminApi';
import { Modal } from './Modal';
import { EcosistemaForm, defaultEcosistema } from './EcosistemaForm';
import { BenchmarkForm, type PendingDelete } from './BenchmarkForm';
import styles from './Admin.module.css';

type ModalTipo = 'create' | 'edit' | 'benchmarks' | 'delete' | null;

export function EcosistemasTable() {
  const { data, loading, error, refetch } = useApi(() => adminApi.getEcosistemas(), []);
  const { data: indicadores } = useApi(() => adminApi.getIndicadores(), []);

  const [search, setSearch] = useState('');
  const [modal, setModal] = useState<ModalTipo>(null);
  const [selected, setSelected] = useState<Ecosistema | null>(null);
  const [form, setForm] = useState(defaultEcosistema());
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');

  // Estado del form de benchmarks (BenchmarkForm reporta cambios hacia aquí)
  const [benchAnio, setBenchAnio] = useState(new Date().getFullYear());
  const [benchValores, setBenchValores] = useState<Record<number, string>>({});
  const [benchPendingDeletes, setBenchPendingDeletes] = useState<PendingDelete[]>([]);

  const filtered = useMemo(() => {
    if (!data) return [];
    const q = search.toLowerCase();
    return q ? data.filter((e) => e.nombre.toLowerCase().includes(q) || e.rol.includes(q)) : data;
  }, [data, search]);

  function openCreate() {
    setForm(defaultEcosistema());
    setFormError('');
    setSelected(null);
    setModal('create');
  }

  function openEdit(eco: Ecosistema) {
    setForm({ nombre: eco.nombre, rol: eco.rol });
    setFormError('');
    setSelected(eco);
    setModal('edit');
  }

  function openBenchmarks(eco: Ecosistema) {
    setSelected(eco);
    setFormError('');
    setBenchPendingDeletes([]);
    setModal('benchmarks');
  }

  function openDelete(eco: Ecosistema) {
    setSelected(eco);
    setModal('delete');
  }

  async function handleSave() {
    if (!form.nombre) {
      setFormError('El nombre es obligatorio.');
      return;
    }
    setSaving(true);
    setFormError('');
    try {
      if (modal === 'create') await adminApi.createEcosistema(form);
      else if (modal === 'edit' && selected) await adminApi.updateEcosistema(selected.id, form);
      setModal(null);
      refetch();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Error al guardar');
    } finally {
      setSaving(false);
    }
  }

  async function handleSaveBenchmarks() {
    if (!selected || !indicadores) return;
    setSaving(true);
    setFormError('');
    try {
      // Primero los borrados diferidos
      for (const pd of benchPendingDeletes) {
        await adminApi.deleteBenchmarkValor(selected.id, pd.benchmarkId);
      }
      const idsIndicadoresBorrados = new Set(benchPendingDeletes.map((pd) => pd.indicadorId));

      // Luego el upsert de los valores restantes
      const valoresPayload = indicadores
        .filter((ind) => !idsIndicadoresBorrados.has(ind.id))
        .filter((ind) => benchValores[ind.id] !== undefined && benchValores[ind.id] !== '')
        .map((ind) => ({
          indicador_id: ind.id,
          anio: benchAnio,
          valor: parseFloat(benchValores[ind.id]),
        }));

      if (valoresPayload.length > 0) {
        await adminApi.guardarBenchmarks(selected.id, { anio: benchAnio, valores: valoresPayload });
      }

      setModal(null);
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Error al guardar los valores');
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!selected) return;
    setSaving(true);
    try {
      await adminApi.deleteEcosistema(selected.id);
      setModal(null);
      refetch();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Error al eliminar');
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} height="48px" />)}
      </div>
    );
  }

  return (
    <>
      {error && <p className={styles.errorBanner}>{error}</p>}

      <div className={styles.tableCard}>
        <div className={styles.tableActions}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <input
              className={styles.searchInput}
              placeholder="Buscar..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <span className={styles.count}>{filtered.length} registros</span>
          </div>
          <button className={styles.addBtn} onClick={openCreate}>+ Nuevo ecosistema</button>
        </div>

        <table className={styles.table}>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Rol</th>
              <th>Entries</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr><td colSpan={4} className={styles.empty}>No hay ecosistemas</td></tr>
            )}
            {filtered.map((eco) => (
              <tr key={eco.id}>
                <td style={{ color: 'var(--text-100)', fontWeight: 500 }}>{eco.nombre}</td>
                <td>{eco.rol}</td>
                <td>
                  <button className={styles.editBtn} onClick={() => openBenchmarks(eco)}>
                    Agregar/editar valores
                  </button>
                </td>
                <td>
                  <div className={styles.rowActions}>
                    <button className={styles.editBtn} onClick={() => openEdit(eco)}>Editar</button>
                    <button className={styles.deleteBtn} onClick={() => openDelete(eco)}>Eliminar</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {(modal === 'create' || modal === 'edit') && (
        <Modal
          title={modal === 'create' ? 'Nuevo ecosistema' : `Editar: ${selected?.nombre}`}
          onClose={() => setModal(null)}
          onConfirm={handleSave}
          loading={saving}
        >
          {formError && <p className={styles.errorBanner} style={{ marginBottom: 'var(--space-4)' }}>{formError}</p>}
          <EcosistemaForm value={form} onChange={setForm} />
        </Modal>
      )}

      {modal === 'benchmarks' && selected && (
        <Modal
          title={`Valores de benchmark — ${selected.nombre}`}
          onClose={() => setModal(null)}
          onConfirm={handleSaveBenchmarks}
          confirmLabel="Guardar valores"
          loading={saving}
        >
          {formError && <p className={styles.errorBanner} style={{ marginBottom: 'var(--space-4)' }}>{formError}</p>}
          {!indicadores ? (
            <Skeleton width="100%" height="200px" />
          ) : (
            <BenchmarkForm
              ecosistemaId={selected.id}
              indicadores={indicadores}
              onChange={(anio, valores, pendingDeletes) => {
                setBenchAnio(anio);
                setBenchValores(valores);
                setBenchPendingDeletes(pendingDeletes);
              }}
            />
          )}
        </Modal>
      )}

      {modal === 'delete' && selected && (
        <Modal
          title="Eliminar ecosistema"
          onClose={() => setModal(null)}
          onConfirm={handleDelete}
          confirmLabel="Eliminar"
          loading={saving}
        >
          {formError && <p className={styles.errorBanner} style={{ marginBottom: 'var(--space-4)' }}>{formError}</p>}
          <p style={{ color: 'var(--text-80)', fontSize: 'var(--text-sm)' }}>
            ¿Eliminar <strong style={{ color: 'var(--text-100)' }}>{selected.nombre}</strong>?
            {' '}Esta acción <strong style={{ color: '#fca5a5' }}>no se puede deshacer</strong> y
            también borrará todos sus valores de benchmark asociados.
          </p>
        </Modal>
      )}
    </>
  );
}