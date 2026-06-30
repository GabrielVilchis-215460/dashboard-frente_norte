import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '../../components/layout';
import { Skeleton } from '../../components/ui';
import { useApi } from '../../hooks/useApi';
import { adminApi, authStorage } from '../../services/adminApi';
import type { Organizacion, Programa } from '../../services/adminApi';
import { Modal } from './Modal';
import { OrgForm, defaultOrg, orgToForm } from './OrgForm';
import { ProgramaForm, defaultPrograma, programaToForm } from './ProgramaForm';
import styles from './Admin.module.css';

type Tab = 'organizaciones' | 'programas';

// ── Tabla de Organizaciones ───────────────────────────────────────────────────

function OrgsTable() {
  const { data, loading, error, refetch } = useApi(() => adminApi.getOrganizaciones(), []);
  const [search, setSearch] = useState('');
  const [modal, setModal] = useState<'create' | 'edit' | 'toggle' | null>(null);
  const [selected, setSelected] = useState<Organizacion | null>(null);
  const [form, setForm] = useState(defaultOrg());
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');
  const [exporting, setExporting] = useState(false);

  async function handleExport() {
    setExporting(true);
    try { await adminApi.exportOrganizaciones(); }
    catch { /* el interceptor ya muestra el error */ }
    finally { setExporting(false); }
  }

  const filtered = useMemo(() => {
    if (!data) return [];
    const q = search.toLowerCase();
    return q ? data.filter((o) => o.nombre.toLowerCase().includes(q) || o.tipo?.toLowerCase().includes(q)) : data;
  }, [data, search]);

  function openCreate() {
    setForm(defaultOrg());
    setFormError('');
    setSelected(null);
    setModal('create');
  }

  function openEdit(org: Organizacion) {
    setForm(orgToForm(org));
    setFormError('');
    setSelected(org);
    setModal('edit');
  }

  function openToggle(org: Organizacion) {
    setSelected(org);
    setModal('toggle');
  }

  async function handleSave() {
    if (!form.nombre || !form.tipo) { setFormError('Nombre y tipo son obligatorios.'); return; }
    setSaving(true);
    setFormError('');
    try {
      if (modal === 'create') await adminApi.createOrganizacion(form as any);
      else if (modal === 'edit' && selected) await adminApi.updateOrganizacion(selected.id, form as any);
      setModal(null);
      refetch();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Error al guardar');
    } finally {
      setSaving(false);
    }
  }

  async function handleToggle() {
    if (!selected) return;
    setSaving(true);
    try {
      await adminApi.toggleOrganizacion(selected.id);
      setModal(null);
      refetch();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Error al cambiar estado');
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} height="48px" />)}</div>;

  return (
    <>
      {error && <p className={styles.errorBanner}>{error}</p>}

      <div className={styles.tableCard}>
        <div className={styles.tableActions}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <input className={styles.searchInput} placeholder="Buscar..." value={search} onChange={(e) => setSearch(e.target.value)} />
            <span className={styles.count}>{filtered.length} registros</span>
          </div>
          <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
            <button className={styles.exportBtn} onClick={handleExport} disabled={exporting}>
              {exporting ? 'Exportando…' : '↓ Exportar CSV'}
            </button>
            <button className={styles.addBtn} onClick={openCreate}>+ Nueva organización</button>
          </div>
        </div>

        <table className={styles.table}>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Tipo</th>
              <th>Zona</th>
              <th>Áreas STEM</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr><td colSpan={6} className={styles.empty}>No hay organizaciones</td></tr>
            )}
            {filtered.map((org) => (
              <tr key={org.id}>
                <td style={{ color: 'var(--text-100)', fontWeight: 500 }}>{org.nombre}</td>
                <td>{org.tipo ?? '—'}</td>
                <td>{org.zona ?? '—'}</td>
                <td>{org.areas_stem?.slice(0, 2).join(', ') ?? '—'}{(org.areas_stem?.length ?? 0) > 2 ? '...' : ''}</td>
                <td>
                  <span className={`${styles.pill} ${org.activo ? styles.pillActive : styles.pillInactive}`}>
                    {org.activo ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td>
                  <div className={styles.rowActions}>
                    <button className={styles.editBtn} onClick={() => openEdit(org)}>Editar</button>
                    <button className={`${styles.deleteBtn}`} onClick={() => openToggle(org)}>
                      {org.activo ? 'Desactivar' : 'Activar'}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {(modal === 'create' || modal === 'edit') && (
        <Modal
          title={modal === 'create' ? 'Nueva organización' : `Editar: ${selected?.nombre}`}
          onClose={() => setModal(null)}
          onConfirm={handleSave}
          loading={saving}
        >
          {formError && <p className={styles.errorBanner} style={{ marginBottom: 'var(--space-4)' }}>{formError}</p>}
          <OrgForm value={form} onChange={setForm} />
        </Modal>
      )}

      {modal === 'toggle' && selected && (
        <Modal
          title={selected.activo ? 'Desactivar organización' : 'Activar organización'}
          onClose={() => setModal(null)}
          onConfirm={handleToggle}
          confirmLabel={selected.activo ? 'Desactivar' : 'Activar'}
          loading={saving}
        >
          <p style={{ color: 'var(--text-80)', fontSize: 'var(--text-sm)' }}>
            {selected.activo
              ? <>¿Desactivar <strong style={{ color: 'var(--text-100)' }}>{selected.nombre}</strong>? Dejará de aparecer en el dashboard pero sus datos se conservan.</>
              : <>¿Reactivar <strong style={{ color: 'var(--text-100)' }}>{selected.nombre}</strong>? Volverá a aparecer en el dashboard.</>
            }
          </p>
        </Modal>
      )}
    </>
  );
}

// ── Tabla de Programas ────────────────────────────────────────────────────────

function ProgramasTable() {
  const { data: programas, loading: loadingP, error: errorP, refetch: refetchP } = useApi(() => adminApi.getProgramas(), []);
  const { data: orgs, loading: loadingO } = useApi(() => adminApi.getOrganizaciones(), []);
  const [search, setSearch] = useState('');
  const [modal, setModal] = useState<'create' | 'edit' | 'toggle' | null>(null);
  const [selected, setSelected] = useState<Programa | null>(null);
  const [form, setForm] = useState(defaultPrograma());
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');
  const [exporting, setExporting] = useState(false);

  async function handleExport() {
    setExporting(true);
    try { await adminApi.exportProgramas(); }
    catch { /* el interceptor ya muestra el error */ }
    finally { setExporting(false); }
  }

  const orgMap = useMemo(() => {
    const m: Record<number, string> = {};
    orgs?.forEach((o) => { m[o.id] = o.nombre; });
    return m;
  }, [orgs]);

  const filtered = useMemo(() => {
    if (!programas) return [];
    const q = search.toLowerCase();
    return q
      ? programas.filter((p) => p.nombre?.toLowerCase().includes(q) || orgMap[p.organizacion_id]?.toLowerCase().includes(q))
      : programas;
  }, [programas, search, orgMap]);

  function openCreate() {
    setForm(defaultPrograma());
    setFormError('');
    setSelected(null);
    setModal('create');
  }

  function openEdit(p: Programa) {
    setForm(programaToForm(p));
    setFormError('');
    setSelected(p);
    setModal('edit');
  }

  function openToggle(p: Programa) {
    setSelected(p);
    setModal('toggle');
  }

  async function handleSave() {
    if (!form.organizacion_id) { setFormError('Debes seleccionar una organización.'); return; }
    setSaving(true);
    setFormError('');
    try {
      if (modal === 'create') await adminApi.createPrograma(form as any);
      else if (modal === 'edit' && selected) await adminApi.updatePrograma(selected.id, form as any);
      setModal(null);
      refetchP();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Error al guardar');
    } finally {
      setSaving(false);
    }
  }

  async function handleToggle() {
    if (!selected) return;
    setSaving(true);
    try {
      await adminApi.togglePrograma(selected.id);
      setModal(null);
      refetchP();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Error al cambiar estado');
    } finally {
      setSaving(false);
    }
  }

  if (loadingP || loadingO) return <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} height="48px" />)}</div>;

  return (
    <>
      {errorP && <p className={styles.errorBanner}>{errorP}</p>}

      <div className={styles.tableCard}>
        <div className={styles.tableActions}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <input className={styles.searchInput} placeholder="Buscar..." value={search} onChange={(e) => setSearch(e.target.value)} />
            <span className={styles.count}>{filtered.length} registros</span>
          </div>
          <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
            <button className={styles.exportBtn} onClick={handleExport} disabled={exporting}>
              {exporting ? 'Exportando…' : '↓ Exportar CSV'}
            </button>
            <button className={styles.addBtn} onClick={openCreate}>+ Nuevo programa</button>
          </div>
        </div>

        <table className={styles.table}>
          <thead>
            <tr>
              <th>Programa</th>
              <th>Organización</th>
              <th>Modalidad</th>
              <th>Madurez</th>
              <th>% Mujeres</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr><td colSpan={7} className={styles.empty}>No hay programas</td></tr>
            )}
            {filtered.map((p) => (
              <tr key={p.id}>
                <td style={{ color: 'var(--text-100)', fontWeight: 500 }}>{p.nombre ?? '(sin nombre)'}</td>
                <td>{orgMap[p.organizacion_id] ?? '—'}</td>
                <td>{p.modalidad ?? '—'}</td>
                <td>{p.madurez ?? '—'}</td>
                <td>{p.pct_mujeres_rango ?? (p.pct_mujeres_mid != null ? `${p.pct_mujeres_mid}%` : '—')}</td>
                <td>
                  <span className={`${styles.pill} ${p.activo ? styles.pillActive : styles.pillInactive}`}>
                    {p.activo ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td>
                  <div className={styles.rowActions}>
                    <button className={styles.editBtn} onClick={() => openEdit(p)}>Editar</button>
                    <button className={styles.deleteBtn} onClick={() => openToggle(p)}>
                      {p.activo ? 'Desactivar' : 'Activar'}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {(modal === 'create' || modal === 'edit') && (
        <Modal
          title={modal === 'create' ? 'Nuevo programa' : `Editar: ${selected?.nombre ?? 'programa'}`}
          onClose={() => setModal(null)}
          onConfirm={handleSave}
          loading={saving}
        >
          {formError && <p className={styles.errorBanner} style={{ marginBottom: 'var(--space-4)' }}>{formError}</p>}
          <ProgramaForm value={form} onChange={setForm} organizaciones={orgs ?? []} />
        </Modal>
      )}

      {modal === 'toggle' && selected && (
        <Modal
          title={selected.activo ? 'Desactivar programa' : 'Activar programa'}
          onClose={() => setModal(null)}
          onConfirm={handleToggle}
          confirmLabel={selected.activo ? 'Desactivar' : 'Activar'}
          loading={saving}
        >
          <p style={{ color: 'var(--text-80)', fontSize: 'var(--text-sm)' }}>
            {selected.activo
              ? <>¿Desactivar <strong style={{ color: 'var(--text-100)' }}>{selected.nombre ?? 'este programa'}</strong>? Dejará de aparecer en el dashboard pero sus datos se conservan.</>
              : <>¿Reactivar <strong style={{ color: 'var(--text-100)' }}>{selected.nombre ?? 'este programa'}</strong>? Volverá a aparecer en el dashboard.</>
            }
          </p>
        </Modal>
      )}
    </>
  );
}

// ── Panel principal ───────────────────────────────────────────────────────────

export function Admin() {
  const [tab, setTab] = useState<Tab>('organizaciones');
  const navigate = useNavigate();

  function logout() {
    authStorage.clearToken();
    navigate('/admin/login', { replace: true });
  }

  return (
    <div>
      <div className={styles.header}>
        <PageHeader
          title="Panel de Administración"
          description="Gestión de organizaciones y programas del ecosistema STEM"
        />
        <button className={styles.logoutBtn} onClick={logout}>Cerrar sesión</button>
      </div>

      <div className={styles.tabs}>
        <button className={`${styles.tab} ${tab === 'organizaciones' ? styles.tabActive : ''}`} onClick={() => setTab('organizaciones')}>
          Organizaciones
        </button>
        <button className={`${styles.tab} ${tab === 'programas' ? styles.tabActive : ''}`} onClick={() => setTab('programas')}>
          Programas
        </button>
      </div>

      {tab === 'organizaciones' ? <OrgsTable /> : <ProgramasTable />}
    </div>
  );
}
