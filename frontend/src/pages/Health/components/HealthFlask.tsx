// Matraz animado que se llena según el score ISE

import { useEffect, useState } from 'react';
import styles from './HealthFlask.module.css';

interface Props {
  score: number;
  nivel: string;
  loading?: boolean;
}

export function HealthFlask({ score, nivel, loading = false }: Props) {
  // Animar el llenado 
  const [fillLevel, setFillLevel] = useState(0);
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    if (loading) return;
    // Pequeño delay
    const t = setTimeout(() => setFillLevel(score), 100);

    // Conteo animado del número
    const duration = 1000;
    const start = performance.now();
    let raf = 0;
    const tick = (now: number) => {
      const progress = Math.min((now - start) / duration, 1);
      setDisplayScore(score * progress);
      if (progress < 1) raf = requestAnimationFrame(tick);
    };
    const t2 = setTimeout(() => { raf = requestAnimationFrame(tick); }, 200);

    return () => {
      clearTimeout(t);
      clearTimeout(t2);
      cancelAnimationFrame(raf);
    };
  }, [score, loading]);

  // Geometría del frasco
  // cuerpo del matraz 
  const BODY_TOP = 80;
  const BODY_BOTTOM = 220;
  const bodyHeight = BODY_BOTTOM - BODY_TOP;
  // Nivel del líquido
  const liquidY = BODY_BOTTOM - (bodyHeight * fillLevel) / 100;

  return (
    <div className={styles.wrapper}>
      <div className={styles.flaskArea}>
        <svg viewBox="0 0 200 240" className={styles.flaskSvg}>
          <defs>
            {/* Clip con la forma del matraz para recortar el líquido */}
            <clipPath id="flask-clip">
              <path d="
                M 78 40
                L 78 95
                C 78 100, 76 104, 72 110
                L 42 168
                C 32 185, 38 212, 60 218
                L 60 218
                C 75 223, 125 223, 140 218
                C 162 212, 168 185, 158 168
                L 128 110
                C 124 104, 122 100, 122 95
                L 122 40
                Z
              " />
            </clipPath>

            {/* Gradiente del líquido */}
            <linearGradient id="liquid-grad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--accent-a)" stopOpacity="0.9" />
              <stop offset="100%" stopColor="var(--accent-c)" stopOpacity="0.95" />
            </linearGradient>
          </defs>

          {/* Líquido recortado por la forma del matraz */}
          <g clipPath="url(#flask-clip)">
            {/* Rectángulo base del líquido */}
            <rect
              x="0"
              y={liquidY}
              width="200"
              height={BODY_BOTTOM - liquidY + 10}
              fill="url(#liquid-grad)"
              className={styles.liquidBody}
            />
            {/* Onda superior animada — dos capas para profundidad */}
            <path
              className={styles.wave1}
              fill="url(#liquid-grad)"
              d={wavePath(liquidY)}
            />
            <path
              className={styles.wave2}
              fill="var(--accent-a)"
              fillOpacity="0.4"
              d={wavePath(liquidY)}
            />
          </g>

          {/* Contorno del matraz */}
          <path
            d="
              M 78 40
              L 78 95
              C 78 100, 76 104, 72 110
              L 42 168
              C 32 185, 38 212, 60 218
              C 75 223, 125 223, 140 218
              C 162 212, 168 185, 158 168
              L 128 110
              C 124 104, 122 100, 122 95
              L 122 40
            "
            fill="none"
            stroke="rgba(255,255,255,0.5)"
            strokeWidth="2.5"
            strokeLinejoin="round"
          />
          {/* Boca del matraz */}
          <line
            x1="72" y1="40" x2="128" y2="40"
            stroke="rgba(255,255,255,0.5)"
            strokeWidth="2.5"
            strokeLinecap="round"
          />
        </svg>

        {/* Texto central sobre el frasco */}
        <div className={styles.scoreOverlay}>
          <span className={styles.score}>
            {displayScore.toFixed(1)} <span className={styles.scoreMax}>/ 100</span>
          </span>
          <span className={styles.nivel}>Nivel: {nivel || '—'}</span>
        </div>
      </div>
    </div>
  );
}

// Genera un path de onda
function wavePath(y: number): string {
  const amp = 9;
  return `
    M -20 ${y}
    Q 5 ${y - amp}, 30 ${y}
    T 80 ${y}
    T 130 ${y}
    T 180 ${y}
    T 230 ${y}
    L 230 240 L -20 240 Z
  `;
}