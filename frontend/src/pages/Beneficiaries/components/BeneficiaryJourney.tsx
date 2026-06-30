// Recorrido del beneficiario STEM

import {
  IconUserSearch,
  IconClipboardCheck,
  IconBooks,
  IconTool,
  IconChartBar,
  IconCertificate,
  IconChevronRight,
} from '@tabler/icons-react';
import { JOURNEY_STEPS } from './journeyData';
import styles from './BeneficiaryJourney.module.css';

const ICON_MAP: Record<string, React.ComponentType<any>> = {
  IconUserSearch,
  IconClipboardCheck,
  IconBooks,
  IconTool,
  IconChartBar,
  IconCertificate,
};

function StepIcon({ name }: { name: string }) {
  const Icon = ICON_MAP[name];
  return Icon ? <Icon size={26} stroke={1.5} /> : null;
}

export function BeneficiaryJourney() {
  return (
    <div className={styles.journey}>
      {JOURNEY_STEPS.map((step, index) => (
        <div key={step.step} className={styles.stepWrapper}>
          <div
            className={`${styles.step} animate-fade-in-up`}
            style={{ animationDelay: `${index * 80}ms` }}
          >
            {/* Icono circular con color por paso */}
            <div
              className={styles.iconCircle}
              data-step={step.step}
              aria-hidden="true"
            >
              <StepIcon name={step.icon} />
            </div>

            <span className={styles.stepNumber} data-step={step.step}>
              {step.step}
            </span>
            <h4 className={styles.stepTitle}>{step.title}</h4>
            <p className={styles.stepDesc}>{step.description}</p>
          </div>

          {/* Chevron entre pasos (no en el último) */}
          {index < JOURNEY_STEPS.length - 1 && (
            <div className={styles.chevron} aria-hidden="true">
              <IconChevronRight size={18} stroke={1.5} />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}