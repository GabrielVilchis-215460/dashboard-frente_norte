import { useState, useMemo, useRef } from 'react';
import { Skeleton } from '../../components/ui';
import { Modal } from './Modal';
import { useApi } from '../../hooks/useApi';
import { adminApi } from '../../services/adminApi';
import type { Organizacion } from '../../services/adminApi';
import type { Evento, EventoCreate } from '../../types';
import { formatFechaEvento, formatHorario } from '../../utils/format';
import styles from './Admin.module.css';

// ── Form de evento ────────────────────────────────────────────────────────────

interface EventoForm {
  nombre: string;
  descripcion: string;
  ubicacion: string;
  fecha: string;
  fecha_fin: string;
  hora_inicio: string;
  hora_fin: string;
  enfoque: string;
  tipo: string;
  imagen_url: string;
  url_original: string;
  organizacion_id: string;
}

function defaultEvento(): EventoForm {
  return {
    nombre: '',
    descripcion: '',
    ubicacion: '',
    fecha: '',
    fecha_fin: '',
    hora_inicio: '',
    hora_fin: '',
    enfoque: '',
    tipo: '',
    imagen_url: '',
    url_original: '',
    organizacion_id: '',
  };
}

function eventoToForm(ev: Evento): EventoForm {
  return {
    nombre: ev.nombre ?? '',
    descripcion: ev.descripcion ?? '',
    ubicacion: ev.ubicacion ?? '',
    fecha: ev.fecha ?? '',
    fecha_fin: ev.fecha_fin ?? '',
    hora_inicio: ev.hora_inicio?.slice(0, 5) ?? '',
    hora_fin: ev.hora_fin?.slice(0, 5) ?? '',
    enfoque: ev.enfoque ?? '',
    tipo: ev.tipo ?? '',
    imagen_url: ev.imagen_url ?? '',
    url_original: ev.url_original ?? '',
    organizacion_id: ev.organizacion?.id?.toString() ?? '',
  };
}

function formToPayload(f: EventoForm): EventoCreate {
  return {
    nombre: f.nombre,
    descripcion: f.descripcion || undefined,
    ubicacion: f.ubicacion || undefined,
    fecha: f.fecha,
    fecha_fin: f.fecha_fin || undefined,
    hora_inicio: f.hora_inicio || undefined,
    hora_fin: f.hora_fin || undefined,
    enfoque: f.enfoque || undefined,
    tipo: f.tipo || undefined,
    imagen_url: f.imagen_url || undefined,
    url_original: f.url_original || undefined,
    organizacion_id: f.organizacion_id ? parseInt(f.organizacion_id) : undefined,
  };
}

// ── Form UI ───────────────────────────────────────────────────────────────────

function EventoFormFields({
  value,
  onChange,
  orgs,
  onImageUpload,
  uploading,
}: {
  value: EventoForm;
  onChange: (v: EventoForm) => void;
  orgs: Organizacion[];
  onImageUpload: (file: File) => void;
  uploading: boolean;
}) {
  const fileRef = useRef<HTMLInputElement>(null);
  const set = (k: keyof EventoForm) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    onChange({ ...value, [k]: e.target.value });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
      <div style={row}>
        <label style={label}>Nombre *</label>
        <input style={input} value={value.nombre} onChange={set('nombre')} placeholder="Nombre del evento" />
      </div>
      <div style={row}>
        <label style={label}>Organización</label>
        <select style={input} value={value.organizacion_id} onChange={set('organizacion_id')}>
          <option value="">Sin organización</option>
          {orgs.map((o) => <option key={o.id} value={o.id}>{o.nombre}</option>)}
        </select>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
        <div style={row}>
          <label style={label}>Fecha inicio *</label>
          <input style={input} type="date" value={value.fecha} onChange={set('fecha')} />
        </div>
        <div style={row}>
          <label style={label}>Fecha fin (multi-día)</label>
          <input style={input} type="date" value={value.fecha_fin} onChange={set('fecha_fin')} min={value.fecha} />
        </div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
        <div style={row}>
          <label style={label}>Hora inicio</label>
          <input style={input} type="time" value={value.hora_inicio} onChange={set('hora_inicio')} />
        </div>
        <div style={row}>
          <label style={label}>Hora fin</label>
          <input style={input} type="time" value={value.hora_fin} onChange={set('hora_fin')} />
        </div>
      </div>
      <div style={row}>
        <label style={label}>Descripción</label>
        <textarea
          style={{ ...input, minHeight: 80, resize: 'vertical' }}
          value={value.descripcion}
          onChange={set('descripcion')}
          placeholder="Descripción del evento"
        />
      </div>
      <div style={row}>
        <label style={label}>Ubicación</label>
        <input style={input} value={value.ubicacion} onChange={set('ubicacion')} placeholder="Nombre del lugar" />
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
        <div style={row}>
          <label style={label}>Tipo</label>
          <input style={input} value={value.tipo} onChange={set('tipo')} placeholder="Ej: Taller, Conferencia…" />
        </div>
        <div style={row}>
          <label style={label}>Enfoque</label>
          <input style={input} value={value.enfoque} onChange={set('enfoque')} placeholder="Ej: STEM, Género…" />
        </div>
      </div>
      <div style={row}>
        <label style={label}>Enlace publicación</label>
        <input style={input} value={value.url_original} onChange={set('url_original')} placeholder="https://…" />
      </div>
      <div style={row}>
        <label style={label}>Imagen de portada</label>
        <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center' }}>
          <input style={{ ...input, flex: 1 }} value={value.imagen_url} onChange={set('imagen_url')} placeholder="URL o sube una imagen" />
          <button
            type="button"
            style={uploadBtn}
            disabled={uploading}
            onClick={() => fileRef.current?.click()}
          >
            {uploading ? 'Subiendo…' : '↑ Subir'}
          </button>
          <input
            ref={fileRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            style={{ display: 'none' }}
            onChange={(e) => { const f = e.target.files?.[0]; if (f) onImageUpload(f); }}
          />
        </div>
        {value.imagen_url && (
          <img src={value.imagen_url} alt="preview" style={{ marginTop: 8, height: 80, borderRadius: 6, objectFit: 'cover' }} />
        )}
      </div>
    </div>
  );
}

const row: React.CSSProperties = { display: 'flex', flexDirection: 'column', gap: 4 };
const label: React.CSSProperties = { fontSize: 12, color: 'var(--text-60)', fontWeight: 500 };
const input: React.CSSProperties = {
  background: 'rgba(255,255,255,0.07)',
  border: '1px solid var(--glass-border)',
  borderRadius: 'var(--radius-md)',
  padding: '8px 12px',
  color: 'var(--text-100)',
  fontSize: 14,
  fontFamily: 'var(--font-body)',
  outline: 'none',
  width: '100%',
  boxSizing: 'border-box',
};
const uploadBtn: React.CSSProperties = {
  background: 'rgba(56,189,248,0.15)',
  border: '1px solid var(--accent-a)',
  color: 'var(--accent-a)',
  borderRadius: 'var(--radius-md)',
  padding: '8px 14px',
  fontSize: 13,
  cursor: 'pointer',
  whiteSpace: 'nowrap',
  fontFamily: 'var(--font-body)',
};

// ── Tabla principal ───────────────────────────────────────────────────────────

export function EventosTable() {
  const { data, loading, error, refetch } = useApi(() => adminApi.getEventosAdmin(), []);
  const { data: orgs } = useApi(() => adminApi.getOrganizaciones(), []);
  const [search, setSearch] = useState('');
  const [modal, setModal] = useState<'create' | 'edit' | 'toggle' | null>(null);
  const [selected, setSelected] = useState<Evento | null>(null);
  const [form, setForm] = useState<EventoForm>(defaultEvento());
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [formError, setFormError] = useState('');

  const filtered = useMemo(() => {
    if (!data) return [];
    const q = search.toLowerCase();
    return q
      ? data.filter((e) =>
          e.nombre.toLowerCase().includes(q) ||
          e.organizacion?.nombre.toLowerCase().includes(q)
        )
      : data;
  }, [data, search]);

  function openCreate() {
    setForm(defaultEvento());
    setFormError('');
    setSelected(null);
    setModal('create');
  }

  function openEdit(ev: Evento) {
    setForm(eventoToForm(ev));
    setFormError('');
    setSelected(ev);
    setModal('edit');
  }

  function openToggle(ev: Evento) {
    setSelected(ev);
    setModal('toggle');
  }

  async function handleImageUpload(file: File) {
    setUploading(true);
    try {
      const url = await adminApi.uploadImagenEvento(file);
      setForm((f) => ({ ...f, imagen_url: url }));
    } catch {
      setFormError('Error al subir la imagen. Verifica que sea JPG, PNG o WebP y menor a 5 MB.');
    } finally {
      setUploading(false);
    }
  }

  async function handleSave() {
    if (!form.nombre || !form.fecha) {
      setFormError('Nombre y fecha son obligatorios.');
      return;
    }
    if (form.fecha_fin && form.fecha_fin < form.fecha) {
      setFormError('La fecha de fin debe ser igual o posterior a la fecha de inicio.');
      return;
    }
    setSaving(true);
    setFormError('');
    try {
      const payload = formToPayload(form);
      if (modal === 'create') {
        await adminApi.createEvento(payload);
      } else if (modal === 'edit' && selected) {
        await adminApi.updateEvento(selected.id, payload);
      }
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
      await adminApi.toggleEvento(selected.id);
      setModal(null);
      refetch();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Error al cambiar estado');
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} height="48px" />)}
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
              placeholder="Buscar evento u organización…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <span className={styles.count}>{filtered.length} eventos</span>
          </div>
          <button className={styles.addBtn} onClick={openCreate}>+ Nuevo evento</button>
        </div>

        <table className={styles.table}>
          <thead>
            <tr>
              <th>Evento</th>
              <th>Fecha</th>
              <th>Horario</th>
              <th>Organización</th>
              <th>Tipo</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr><td colSpan={7} className={styles.empty}>No hay eventos</td></tr>
            )}
            {filtered.map((ev) => (
              <tr key={ev.id}>
                <td style={{ color: 'var(--text-100)', fontWeight: 500, maxWidth: 200 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    {ev.imagen_url && (
                      <img src={ev.imagen_url} alt="" style={{ width: 32, height: 32, borderRadius: 4, objectFit: 'cover', flexShrink: 0 }} />
                    )}
                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {ev.nombre}
                    </span>
                  </div>
                </td>
                <td style={{ whiteSpace: 'nowrap' }}>{formatFechaEvento(ev.fecha, ev.fecha_fin)}</td>
                <td style={{ whiteSpace: 'nowrap' }}>{formatHorario(ev.hora_inicio, ev.hora_fin) || '—'}</td>
                <td>{ev.organizacion?.nombre ?? '—'}</td>
                <td>{ev.tipo ?? '—'}</td>
                <td>
                  <span className={`${styles.pill} ${ev.activo ? styles.pillActive : styles.pillInactive}`}>
                    {ev.activo ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td>
                  <div className={styles.rowActions}>
                    <button className={styles.editBtn} onClick={() => openEdit(ev)}>Editar</button>
                    <button className={styles.deleteBtn} onClick={() => openToggle(ev)}>
                      {ev.activo ? 'Desactivar' : 'Activar'}
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
          title={modal === 'create' ? 'Nuevo evento' : `Editar: ${selected?.nombre}`}
          onClose={() => setModal(null)}
          onConfirm={handleSave}
          loading={saving}
        >
          {formError && <p className={styles.errorBanner} style={{ marginBottom: 'var(--space-4)' }}>{formError}</p>}
          <EventoFormFields
            value={form}
            onChange={setForm}
            orgs={orgs ?? []}
            onImageUpload={handleImageUpload}
            uploading={uploading}
          />
        </Modal>
      )}

      {modal === 'toggle' && selected && (
        <Modal
          title={selected.activo ? 'Desactivar evento' : 'Activar evento'}
          onClose={() => setModal(null)}
          onConfirm={handleToggle}
          confirmLabel={selected.activo ? 'Desactivar' : 'Activar'}
          loading={saving}
        >
          <p style={{ color: 'var(--text-80)', fontSize: 'var(--text-sm)' }}>
            {selected.activo
              ? <>¿Desactivar <strong style={{ color: 'var(--text-100)' }}>{selected.nombre}</strong>? Dejará de aparecer en el dashboard pero se conserva en el historial.</>
              : <>¿Reactivar <strong style={{ color: 'var(--text-100)' }}>{selected.nombre}</strong>? Volverá a aparecer como evento activo.</>
            }
          </p>
        </Modal>
      )}
    </>
  );
}
