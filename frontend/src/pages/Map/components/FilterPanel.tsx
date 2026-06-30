// Panel de filtros del mapa

import { IconFilter, IconX, IconChevronDown, IconChevronUp } from '@tabler/icons-react';
import { FILTER_GROUPS } from './mapConfig';
import type { MapFilters } from '../../../types';
import styles from './FilterPanel.module.css';

interface Props {
  filters: MapFilters;
  onChange: (key: keyof MapFilters, value: string | undefined) => void;
  onClear: () => void;
  open: boolean;
  onToggle: () => void;
}

export function FilterPanel({ filters, onChange, onClear, open, onToggle }: Props) {
  const activeCount = Object.entries(filters)
    .filter(([k, v]) => k !== 'solo_con_coordenadas' && v)
    .length;

  return (
    <div className={styles.wrapper}>
      {/* Trigger button — único, no se duplica dentro del panel */}
      <button className={styles.triggerBtn} onClick={onToggle}>
        <IconFilter size={16} stroke={1.5} />
        Filtros
        {activeCount > 0 && (
          <span className={styles.badge}>{activeCount}</span>
        )}
        {open
          ? <IconChevronUp size={14} stroke={2} />
          : <IconChevronDown size={14} stroke={2} />
        }
      </button>

      {/* Panel desplegable */}
      {open && (
        <div className={styles.panel}>
          <div className={styles.panelHeader}>
            <button className={styles.clearBtn} onClick={onClear}>
              Limpiar filtros
            </button>
          </div>

          <div className={styles.groups}>
            {FILTER_GROUPS.map((group) => {
              const currentVal = filters[group.queryParam as keyof MapFilters] as string | undefined;
              return (
                <div key={group.key} className={styles.group}>
                  <h4 className={styles.groupLabel}>{group.label}</h4>
                  <div className={styles.chips}>
                    {group.options.map((opt) => {
                      const active = currentVal === opt.value;
                      return (
                        <button
                          key={opt.value}
                          className={`${styles.chip} ${active ? styles.chipActive : ''}`}
                          onClick={() =>
                            onChange(
                              group.queryParam as keyof MapFilters,
                              active ? undefined : opt.value
                            )
                          }
                        >
                          {active && <IconX size={11} stroke={2} />}
                          {opt.label}
                        </button>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}