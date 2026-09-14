import { useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { IconInfoCircle } from '@tabler/icons-react';
import styles from './InfoTooltip.module.css';

interface Props {
  text?: string;
}

const POPOVER_MAX_WIDTH = 220;
const EDGE_PADDING = 12;

export function InfoTooltip({ text = 'Información contextual pendiente.' }: Props) {
  const [open, setOpen] = useState(false);
  const [pos, setPos] = useState({ top: 0, left: 0 });
  const iconRef = useRef<HTMLSpanElement>(null);

  function handleEnter() {
    const rect = iconRef.current?.getBoundingClientRect();
    if (rect) {
      const centerX = rect.left + rect.width / 2;
      const clampedLeft = Math.min(
        Math.max(centerX, POPOVER_MAX_WIDTH / 2 + EDGE_PADDING),
        window.innerWidth - POPOVER_MAX_WIDTH / 2 - EDGE_PADDING
      );
      setPos({ top: rect.bottom + 8, left: clampedLeft });
    }
    setOpen(true);
  }

  return (
    <span
      ref={iconRef}
      className={styles.wrapper}
      onMouseEnter={handleEnter}
      onMouseLeave={() => setOpen(false)}
    >
      <IconInfoCircle size={15} stroke={1.6} className={styles.icon} />

      {open &&
        createPortal(
          <div
            className={styles.popover}
            style={{ top: pos.top, left: pos.left }}
          >
            {text}
          </div>,
          document.body
        )}
    </span>
  );
}