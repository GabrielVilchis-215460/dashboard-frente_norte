// Ficha descriptiva del actor

import {
  IconX,
  IconExternalLink,
  IconPhone,
  IconMail,
  IconMapPin,
  IconUsers,
} from '@tabler/icons-react';
import { getTipoConfig } from './mapConfig';
import { formatLabel } from '../../../utils/format';
import type { FichaActor } from '../../../types';
import styles from './ActorSheet.module.css';

interface Props {
  ficha: FichaActor | null;
  loading: boolean;
  onClose: () => void;
}

export function ActorSheet({ ficha, loading, onClose }: Props) {
  if (!ficha && !loading) return null;

  const tipoConfig = ficha ? getTipoConfig(ficha.tipo) : null;

  return (
    <div className={styles.sheet}>
      {/* Header */}
      <div className={styles.header}>
        <div>
          {tipoConfig && (
            <div className={styles.badges}>
              <span className={styles.tipoBadge} style={{ borderColor: tipoConfig.color, color: tipoConfig.color }}>
                {ficha?.tipo}
              </span>
              {ficha?.enfoque_principal && (
                <span className={styles.enfoqueBadge}>
                  {formatLabel(ficha.enfoque_principal)}
                </span>
              )}
            </div>
          )}
          <h3 className={styles.nombre}>
            {loading ? '...' : ficha?.nombre}
          </h3>
        </div>
        <button className={styles.closeBtn} onClick={onClose} aria-label="Cerrar ficha">
          <IconX size={18} stroke={1.5} />
        </button>
      </div>

      {loading ? (
        <div className={styles.skeleton}>
          <div className={styles.skeletonLine} style={{ width: '80%' }} />
          <div className={styles.skeletonLine} style={{ width: '60%' }} />
          <div className={styles.skeletonLine} style={{ width: '100%' }} />
          <div className={styles.skeletonLine} style={{ width: '90%' }} />
        </div>
      ) : ficha && (
        <div className={styles.body}>
          {/* Descripción */}
          {ficha.descripcion && (
            <p className={styles.descripcion}>{ficha.descripcion}</p>
          )}

          {/* Programas */}
          {ficha.programas.length > 0 && (
            <div className={styles.section}>
              <span className={styles.sectionLabel}>Programas activos</span>
              <ul className={styles.list}>
                {ficha.programas.map((p, i) => (
                  <li key={i} className={styles.listItem}>{p}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Áreas STEM */}
          {ficha.areas_stem.length > 0 && (
            <div className={styles.section}>
              <span className={styles.sectionLabel}>Áreas STEM</span>
              <div className={styles.tags}>
                {ficha.areas_stem.map((a, i) => (
                  <span key={i} className={styles.tag}>{a}</span>
                ))}
              </div>
            </div>
          )}

          {/* Contacto */}
          <div className={styles.section}>
            <span className={styles.sectionLabel}>Contacto</span>
            <div className={styles.contactList}>
              {ficha.contacto_nombre && (
                <div className={styles.contactRow}>
                  <IconUsers size={14} stroke={1.5} />
                  <span>{ficha.contacto_nombre}</span>
                </div>
              )}
              {ficha.contacto_email && (
                <div className={styles.contactRow}>
                  <IconMail size={14} stroke={1.5} />
                  <span>{ficha.contacto_email}</span>
                </div>
              )}
              {ficha.contacto_telefono && (
                <div className={styles.contactRow}>
                  <IconPhone size={14} stroke={1.5} />
                  <span>{ficha.contacto_telefono}</span>
                </div>
              )}
              {ficha.direccion && (
                <div className={styles.contactRow}>
                  <IconMapPin size={14} stroke={1.5} />
                  <span>{ficha.direccion}</span>
                </div>
              )}
              {(!ficha.contacto_nombre && !ficha.contacto_email && !ficha.contacto_telefono && !ficha.direccion) && (
                <span className={styles.noData}>Sin información de contacto</span>
              )}
            </div>
          </div>

          {/* Sitio web */}
          {ficha.sitio_web && (
            <a
              href={ficha.sitio_web}
              target="_blank"
              rel="noopener noreferrer"
              className={styles.webLink}
            >
              <IconExternalLink size={14} stroke={1.5} />
              Visitar sitio web
            </a>
          )}
        </div>
      )}
    </div>
  );
}