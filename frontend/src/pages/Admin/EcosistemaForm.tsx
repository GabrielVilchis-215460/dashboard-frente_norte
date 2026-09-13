import styles from './AdminForm.module.css';
import type { EcosistemaCreate } from '../../services/adminApi';

const ROLES = ['local', 'referente', 'par'];

interface Props {
  value: EcosistemaCreate;
  onChange: (v: EcosistemaCreate) => void;
}

export function EcosistemaForm({ value, onChange }: Props) {
  const set = (key: keyof EcosistemaCreate, val: string) => onChange({ ...value, [key]: val });

  return (
    <div className={styles.grid}>
      <div className={`${styles.fieldGroup} ${styles.fullWidth}`}>
        <label className={styles.label}>Nombre *</label>
        <input
          className={styles.input}
          value={value.nombre}
          onChange={(e) => set('nombre', e.target.value)}
          placeholder="Nombre del ecosistema (ciudad)"
        />
      </div>

      <div className={styles.fieldGroup}>
        <label className={styles.label}>Rol *</label>
        <select
          className={styles.select}
          value={value.rol}
          onChange={(e) => set('rol', e.target.value as EcosistemaCreate['rol'])}
        >
          {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
        </select>
      </div>
    </div>
  );
}

export function defaultEcosistema(): EcosistemaCreate {
  return { nombre: '', rol: 'referente' };
}