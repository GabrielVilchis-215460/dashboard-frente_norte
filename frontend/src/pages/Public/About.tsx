import { IconExternalLink } from '@tabler/icons-react';
import styles from './About.module.css';

const ORGANIZACIONES_COLABORADORAS: { nombre: string; logo: string; url?: string }[] = [
  { nombre: 'CECyTECH Chihuahua', logo: '/partners/cecytech.png', url: undefined },
  { nombre: 'Centro de Estudios Industria 4.0 A.C', logo: '/partners/CEI.svg', url: undefined },
  { nombre: 'CIITA', logo: '/partners/ciita.png', url: undefined },
  { nombre: 'Competitividad Laboral', logo: '/partners/CL.png', url: undefined },
  { nombre: 'CONREDES', logo: '/partners/conredes.png', url: undefined },
  { nombre: 'Coordinación de Política Digital', logo: '/partners/CPD.png', url: undefined },
  { nombre: 'Desarrollo Económico de Ciudad Juárez', logo: '/partners/DECJ.PNG', url: undefined },
  { nombre: 'FECHAC', logo: '/partners/FECHAC.png', url: undefined },
  { nombre: 'FUNAX', logo: '/partners/FUNAX.png', url: undefined },
  { nombre: 'Instituto de Innovación y Competitividad', logo: '/partners/IIC.png', url: undefined },
  { nombre: 'Instituto Promotor de Educación Chihuahua', logo: '/partners/IPE.png', url: undefined },
  { nombre: 'Instituto Tecnológico de Ciudad Juárez', logo: '/partners/ITCJ.png', url: undefined },
  { nombre: 'Microsoft', logo: '/partners/microsoft.png', url: undefined },
  { nombre: 'Red por la Ciberseguridad', logo: '/partners/red-ciberseguridad.png', url: undefined },
  { nombre: 'La Rodadora', logo: '/partners/rodadora.png', url: undefined },
  { nombre: 'Startup Juárez', logo: '/partners/startup-juarez.png', url: undefined },
  { nombre: 'Tecnológico de Monterrey', logo: '/partners/tec-monterrey.png', url: undefined },
  { nombre: 'Universidad Autónoma de Ciudad Juárez', logo: '/partners/UACJ.png', url: undefined },
  { nombre: 'Universidad Tecnológica de Ciudad Juárez', logo: '/partners/UTCJ.png', url: undefined },
];

function PartnerCard({ org }: { org: (typeof ORGANIZACIONES_COLABORADORAS)[number] }) {
  const contenido = <img src={org.logo} alt={org.nombre} className={styles.partnerLogo} />;

  return org.url ? (
    <a
      href={org.url}
      target="_blank"
      rel="noopener noreferrer"
      className={styles.partnerCard}
      title={org.nombre}
    >
      {contenido}
    </a>
  ) : (
    <div className={styles.partnerCard} title={org.nombre}>
      {contenido}
    </div>
  );
}

export function About() {
  return (
    <div className={styles.page}>

      <div className={styles.glass}>
        <section className={styles.hero}>
          <span className={styles.eyebrow}>Acerca de</span>
          <h1 className={styles.title}>El ecosistema STEM en Ciudad Juárez</h1>
          <p className={styles.lead}>
            Ciudad Juárez es uno de los polos industriales y binacionales más importantes
            del norte de México, con una vocación manufacturera que por su naturaleza concentra
            talento técnico y especializado, generando el crecimiento de un nuevo ecosistema en la ciudad.
            Universidades, centros de investigación, empresas, laboratorios y organizaciones civiles son quienes forman a las nuevas
            generaciones en ciencia, tecnología, ingeniería y matemáticas. El objetivo de esta página es hacer visible este esfuerzo
            y apoyar a la comunidad al congregar los eventos de interés en el área STEM en un solo lugar para poder facilitar su conocimiento
            y exponenciar su alcance.
          </p>
        </section>

        <hr className={styles.divider} />

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>El entorno</h2>
          <p className={styles.paragraph}>
            La frontera concentra una de las bases manufactureras más grandes de
            América Latina, y esa vocación industrial está evolucionando hacia
            procesos cada vez más automatizados, digitales y de alto valor
            agregado. Formar a las próximas generaciones en STEM no es solo una
            apuesta educativa: es lo que va a determinar si Ciudad Juárez puede
            retener talento, atraer inversión de mayor complejidad tecnológica y
            ofrecer mejores oportunidades a quienes crecen aquí.
          </p>
          <p className={styles.paragraph}>
            Sin embargo, ese esfuerzo está repartido entre muchas manos: centros
            de investigación, universidades, gobierno, empresas, organizaciones
            civiles y makerspaces trabajan en paralelo, muchas veces sin
            visibilidad de lo que hacen los demás. Esa fragmentación dificulta
            que estudiantes, familias y aliados encuentren los programas y
            eventos que ya existen.
          </p>
        </section>

        <hr className={styles.divider} />

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>El enfoque</h2>
          <p className={styles.paragraph}>
            Este sitio reúne en un solo lugar los eventos, talleres y actividades STEM
            que suceden en Ciudad Juárez, para que sea más fácil encontrarlos, participar
            en ellos y entender qué tan grande y qué tan activa es esta comunidad. En ese sitio
            puedes explorar los eventos en el ecosistema por tema — ciencia, tecnología, ingeniería, robótica, inteligencia
            artificial y más — y descubrir tanto convocatorias abiertas al público como
            iniciativas impulsadas por universidades, centros de investigación, empresas y
            organizaciones civiles que normalmente pasan desapercibidas fuera de sus propios círculos.
          </p>
          <p className={styles.paragraph}>
            Para los estudiantes, familias, docentes, mentores y miembros de la comunidad que buscan estas oportunidades
            significa dejar de depender de enterarse por casualidad o por el boca en boca, y tener un solo punto de partida confiable.
            Para las organizaciones que ya trabajan en esto, significa mayor alcance y la posibilidad de conectar con aliados que
            persiguen objetivos similares. Y para la ciudad en su conjunto, significa poder ver, por primera vez, el tamaño real de
            este esfuerzo colectivo: cuántas manos distintas están formando talento STEM en Juárez, con qué frecuencia, y en qué áreas se está invirtiendo más.
          </p>
        </section>

        <hr className={styles.divider} />

        <section className={styles.partnersSection}>
          <h2 className={styles.sectionTitleCentered}>Organizaciones colaboradoras</h2>

          <div className={styles.partnersMarqueeWrap}>
            <div className={styles.partnersTrack}>
              {/* Arreglo duplicado para infinite scroll*/}
              {ORGANIZACIONES_COLABORADORAS.map((org) => (
                <PartnerCard key={`a-${org.nombre}`} org={org} />
              ))}
              {ORGANIZACIONES_COLABORADORAS.map((org) => (
                <PartnerCard key={`b-${org.nombre}`} org={org} />
              ))}
            </div>
          </div>
        </section>

        <hr className={styles.divider} />

        <a
          href="https://frentenorte.org/"
          target="_blank"
          rel="noopener noreferrer"
          className={styles.siteBtn}
        >
          Visita nuestro sitio oficial
          <IconExternalLink size={18} stroke={1.8} />
        </a>
      </div>

    </div>
  );
}