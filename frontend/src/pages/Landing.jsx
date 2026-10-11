import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Activity, BookOpen, Brain, FileSearch, Layers, Rocket, Sparkles, Target } from 'lucide-react';
import ScoreRing from '../components/ScoreRing.jsx';
import ThemeToggle from '../components/ThemeToggle.jsx';
import { useAuth } from '../lib/auth.jsx';
import { fadeUp, stagger } from '../lib/motion.js';

const FLOW = ['Resume', 'NLP parsing', 'Skill extraction', 'Target role', 'Gap analysis', 'Roadmap', 'Courses', 'Progress', 'Updated profile'];
const FEATURES = [
  { icon: FileSearch, title: 'Resume parsing that understands you', text: 'Upload a PDF or DOCX. We pull out skills, education, certifications and experience and score our confidence in each.' },
  { icon: Target, title: 'Gap analysis against real roles', text: 'Every skill is weighted by importance for the role, with credit for equivalents and related knowledge — not just keyword matching.' },
  { icon: Layers, title: 'A roadmap in the right order', text: 'Prerequisites come first. Your plan is split into time-boxed phases that fit the hours you actually have each week.' },
  { icon: BookOpen, title: 'Courses matched to each gap', text: 'Each step links to a resource at the right level for where you are, with free options preferred.' },
  { icon: Activity, title: 'Progress you can see', text: 'Readiness trends, activity and category breakdowns update as you complete steps and re-analyse.' },
  { icon: Brain, title: 'A loop, not a one-off report', text: 'Skills you complete feed back into your next analysis, so your score reflects what you have actually learned.' },
];

export default function Landing() {
  const { user } = useAuth();
  const cta = user ? { to: '/dashboard', label: 'Open dashboard' } : { to: '/register', label: 'Get started free' };

  return (
    <div>
      <header className="land-nav">
        <Link to="/" className="brand" style={{ color: 'inherit', padding: 0 }}>
          <span className="brand-mark"><Target size={18} /></span>FutureFit <span className="gradient-text">AI</span>
        </Link>
        <div className="row">
          <ThemeToggle />
          {!user && <Link to="/login" className="btn btn-ghost">Sign in</Link>}
          <Link to={cta.to} className="btn btn-primary">{cta.label}</Link>
        </div>
      </header>

      <section className="hero">
        <div className="hero-orb" style={{ width: 420, height: 420, background: 'var(--accent)', top: -80, left: -100 }} />
        <div className="hero-orb" style={{ width: 360, height: 360, background: '#ec4899', bottom: -120, right: 0, animationDelay: '-6s' }} />
        <motion.div variants={stagger(0.1)} initial="hidden" animate="show" className="col" style={{ gap: 22 }}>
          <motion.span variants={fadeUp} className="chip accent" style={{ alignSelf: 'flex-start' }}><Sparkles size={14} /> AI-driven career alignment</motion.span>
          <motion.h1 variants={fadeUp}>Know exactly what stands between you and <span className="gradient-text">your target role.</span></motion.h1>
          <motion.p variants={fadeUp} className="muted" style={{ fontSize: '1.1rem', maxWidth: 560 }}>
            FutureFit AI reads your resume, compares it with what the role demands, and builds a personalised, prerequisite-aware learning roadmap — then tracks your progress as you close the gap.
          </motion.p>
          <motion.div variants={fadeUp} className="row wrap">
            <Link to={cta.to} className="btn btn-primary btn-lg">{cta.label} <ArrowRight size={18} /></Link>
            <a href="#how" className="btn btn-ghost btn-lg">See how it works</a>
          </motion.div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 30, scale: 0.96 }} animate={{ opacity: 1, y: 0, scale: 1 }} transition={{ delay: 0.3, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}>
          <motion.div animate={{ y: [0, -10, 0] }} transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }} className="card col" style={{ alignItems: 'center', gap: 18, padding: 30 }}>
            <div className="row between" style={{ width: '100%' }}><span className="chip accent"><Rocket size={13} /> Example preview</span><span className="muted tiny">Full Stack Developer</span></div>
            <ScoreRing value={72} size={190} label="Nearly there" sublabel="role readiness" />
            <div className="chips" style={{ justifyContent: 'center' }}>
              <span className="chip ok">14 matched</span><span className="chip warn">4 partial</span><span className="chip bad">3 missing</span>
            </div>
          </motion.div>
        </motion.div>
      </section>

      <section className="section" id="how">
        <motion.div variants={stagger(0.05)} initial="hidden" whileInView="show" viewport={{ once: true, margin: '-80px' }} className="col" style={{ gap: 20 }}>
          <motion.div variants={fadeUp}><h1>One closed loop, end to end</h1><p className="muted" style={{ marginTop: 8 }}>Every step feeds the next — and your progress feeds the start.</p></motion.div>
          <div className="flow">
            {FLOW.map((s, i) => (
              <motion.span key={s} variants={fadeUp} className="row" style={{ gap: 10 }}>
                <span className="chip accent">{i + 1}. {s}</span>{i < FLOW.length - 1 && <ArrowRight size={14} className="muted" />}
              </motion.span>
            ))}
          </div>
        </motion.div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <motion.div variants={stagger(0.08)} initial="hidden" whileInView="show" viewport={{ once: true, margin: '-60px' }} className="grid g3">
          {FEATURES.map(({ icon: Icon, title, text }) => (
            <motion.div key={title} variants={fadeUp} whileHover={{ y: -4 }} className="card">
              <div className="feature-icon"><Icon size={22} /></div>
              <h3 style={{ marginBottom: 6 }}>{title}</h3><p className="muted small">{text}</p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <motion.div initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="card col" style={{ alignItems: 'center', textAlign: 'center', padding: '48px 24px', background: 'linear-gradient(135deg, var(--accent-soft), var(--bg-elev))' }}>
          <h1>Ready to see where you stand?</h1>
          <p className="muted" style={{ maxWidth: 480 }}>Upload your resume, pick a role, and get your readiness score and roadmap in seconds.</p>
          <Link to={cta.to} className="btn btn-primary btn-lg">{cta.label} <ArrowRight size={18} /></Link>
        </motion.div>
      </section>

      <footer className="section muted small" style={{ textAlign: 'center', paddingBlock: 28 }}>
        FutureFit AI · Department of Computer Science &amp; Engineering, Echelon Institute of Technology
      </footer>
    </div>
  );
}
