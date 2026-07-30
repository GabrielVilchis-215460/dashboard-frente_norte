import { EcosystemMap } from '../../pages/Map/components/EcosystemMap';
import type { EventoMapPoint } from '../../types';
import styles from './PublicMap.module.css';

interface Props {
  eventPoints: EventoMapPoint[];
  height?: number;
  /** Centro y zoom y count custom */
  center?: [number, number];
  zoom?: number;
  showEventCount?: boolean;
}

/*
 * Reutiliza EcosystemMap (del dashboard) tanto para el mapa general del home 
 * como para el mapa individual del detalle de un evento
 */
export function PublicMap({ eventPoints, height = 380, center, zoom, showEventCount = true }: Props) {
  return (
    <div className={styles.wrapper} style={{ height }}>
      <EcosystemMap
        pins={[]}
        eventPoints={eventPoints}
        mode="events"
        selectedId={null}
        onPinClick={() => {}}
        center={center}
        zoom={zoom}
        showEventCount={showEventCount}
      />
    </div>
  );
}