import { IconExternalLink } from '@tabler/icons-react';
import styles from './About.module.css';

export function About() {
  return (
    <div className={styles.page}>
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
  );
}