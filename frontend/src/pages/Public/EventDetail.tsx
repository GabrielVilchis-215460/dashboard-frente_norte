import { useParams } from 'react-router-dom';

export function EventDetail() {
  const { id } = useParams();
  return (
    <div style={{ padding: 48, color: 'black' }}>
      <h1>Detalle del evento #{id}</h1>
    </div>
  );
}