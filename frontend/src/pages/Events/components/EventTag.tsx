// Tag de tipo/enfoque del evento
import {
  IconTools, IconBook, IconTent, IconCode, IconMicrophone, IconUsersGroup, IconAward, IconPresentation,
  IconMicroscope, IconCpu, IconTool, IconAbacus, IconRobot, IconSparkle,
  IconLeaf, IconCoin, IconRocket, IconTag, IconSchool, IconGlobe,
} from '@tabler/icons-react';
import { TIPO_ICON, ENFOQUE_ICON } from './eventConfig';
import styles from './EventTag.module.css';

const ICON_MAP: Record<string, React.ComponentType<{ size?: number | string; stroke?: number | string }>> = {
  IconTools, IconBook, IconTent, IconCode, IconMicrophone, IconUsersGroup, IconAward, IconPresentation,
  IconMicroscope, IconCpu, IconTool, IconAbacus, IconRobot, IconSparkle,
  IconLeaf, IconCoin, IconRocket, IconTag, IconSchool, IconGlobe,
};

interface Props {
  label: string;
  variant: 'tipo' | 'enfoque';
}

export function EventTag({ label, variant }: Props) {
  const iconName = variant === 'tipo'
    ? (TIPO_ICON[label] ?? 'IconTag')
    : (ENFOQUE_ICON[label] ?? 'IconTag');
  const Icon = ICON_MAP[iconName] ?? IconTag;

  return (
    <span className={`${styles.tag} ${styles[variant]}`}>
      <Icon size={11} stroke={1.8} />
      {label}
    </span>
  );
}