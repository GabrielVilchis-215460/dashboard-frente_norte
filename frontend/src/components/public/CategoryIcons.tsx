import { useNavigate } from 'react-router-dom';
import {
  IconMicroscope, IconCpu, IconTool, IconAbacus, IconRobot, IconSparkle,
  IconLeaf, IconCoin, IconRocket,
} from '@tabler/icons-react';
import { ROUTES } from '../../constants/routes';
import styles from './CategoryIcons.module.css';

const CATEGORIAS = [
  { label: 'Ciencia', icon: IconMicroscope },
  { label: 'Tecnologia', icon: IconCpu },
  { label: 'Ingenieria', icon: IconTool },
  { label: 'Matematicas', icon: IconAbacus },
  { label: 'Robotica', icon: IconRobot },
  { label: 'Inteligencia artificial', icon: IconSparkle },
  { label: 'Medio ambiente', icon: IconLeaf },
  { label: 'Finanzas', icon: IconCoin },
  { label: 'Emprendimiento', icon: IconRocket },
];

export function CategoryIcons() {
  const navigate = useNavigate();

  return (
    <div className={styles.row}>
      {CATEGORIAS.map(({ label, icon: Icon }) => (
        <button
          key={label}
          type="button"
          className={styles.item}
          onClick={() => navigate(`${ROUTES.EVENTS}?enfoque=${encodeURIComponent(label)}`)}
        >
          <span className={styles.iconCircle}>
            <Icon size={26} stroke={1.5} />
          </span>
          <span className={styles.label}>{label}</span>
        </button>
      ))}
    </div>
  );
}