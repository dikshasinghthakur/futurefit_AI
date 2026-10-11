import { useState } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { ArrowRight, Check, Eye, EyeOff, Target } from 'lucide-react';
import { useAuth } from '../lib/auth.jsx';
import ThemeToggle from '../components/ThemeToggle.jsx';

const POINTS = ['Resume parsing with skill-confidence scoring', 'Weighted gap analysis for real job roles', 'Prerequisite-aware roadmap with course picks', 'Progress tracking that feeds your next analysis'];

export default function AuthPage({ mode }) {
  const isRegister = mode === 'register';
  const { user, login, register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [show, setShow] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to={location.state?.from || '/dashboard'} replace />;

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
  const submit = async (e) => {
    e.preventDefault();
    setError(''); setBusy(true);
    try {
      if (isRegister) await register(form.name, form.email, form.password);
      else await login(form.email, form.password);
      navigate(location.state?.from || '/dashboard', { replace: true });
    } catch (err) {
      setError(err.message);
    } finally { setBusy(false); }
  };

  return (
    <div className="auth">
      <div className="auth-art">
        <div className="orb" style={{ width: 340, height: 340, background: '#a5b4fc', top: -90, right: -60 }} />
        <div className="orb" style={{ width: 300, height: 300, background: '#f9a8d4', bottom: -80, left: -60, animationDelay: '-7s' }} />
        <Link to="/" className="brand" style={{ color: '#fff', position: 'relative', padding: 0 }}>
          <span className="brand-mark" style={{ background: 'rgba(255,255,255,.2)', boxShadow: 'none' }}><Target size={18} /></span>FutureFit AI
        </Link>
        <div style={{ position: 'relative' }} className="col">
          <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} style={{ fontSize: '2.4rem', lineHeight: 1.1 }}>
            Turn “where am I?” into a plan.
          </motion.h1>
          <ul style={{ listStyle: 'none', padding: 0, margin: '18px 0 0', display: 'grid', gap: 12 }}>
            {POINTS.map((p, i) => (
              <motion.li key={p} initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.25 + i * 0.1 }} className="row" style={{ gap: 10 }}>
                <span style={{ width: 22, height: 22, borderRadius: '50%', background: 'rgba(255,255,255,.22)', display: 'grid', placeItems: 'center', flex: 'none' }}><Check size={13} /></span>{p}
              </motion.li>
            ))}
          </ul>
        </div>
        <div style={{ position: 'relative', opacity: 0.8 }} className="small">Echelon Institute of Technology · CSE Project</div>
      </div>

      <div className="auth-form">
        <div style={{ position: 'fixed', top: 16, right: 16 }}><ThemeToggle /></div>
        <motion.form onSubmit={submit} className="card col" style={{ width: 'min(420px, 100%)', gap: 16, padding: 30 }}
          initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}>
          <div><h1>{isRegister ? 'Create your account' : 'Welcome back'}</h1>
            <p className="muted" style={{ marginTop: 6 }}>{isRegister ? 'Start closing your skill gap today.' : 'Sign in to continue your roadmap.'}</p></div>

          <AnimatePresence initial={false}>
            {isRegister && (
              <motion.div key="name" className="field" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} style={{ overflow: 'hidden' }}>
                <label htmlFor="name">Full name</label>
                <input id="name" className="input" required minLength={2} autoComplete="name" value={form.name} onChange={set('name')} placeholder="Your name" />
              </motion.div>
            )}
          </AnimatePresence>

          <div className="field"><label htmlFor="email">Email</label>
            <input id="email" type="email" className="input" required autoComplete="email" value={form.email} onChange={set('email')} placeholder="you@example.com" /></div>

          <div className="field"><label htmlFor="password">Password</label>
            <div style={{ position: 'relative' }}>
              <input id="password" type={show ? 'text' : 'password'} className="input" required minLength={isRegister ? 8 : 1} autoComplete={isRegister ? 'new-password' : 'current-password'}
                value={form.password} onChange={set('password')} placeholder={isRegister ? 'At least 8 characters' : 'Your password'} style={{ paddingRight: 44 }} />
              <button type="button" className="btn btn-icon" onClick={() => setShow((s) => !s)} aria-label={show ? 'Hide password' : 'Show password'}
                style={{ position: 'absolute', right: 4, top: 4, background: 'none' }}>{show ? <EyeOff size={17} /> : <Eye size={17} />}</button>
            </div></div>

          <AnimatePresence>
            {error && <motion.div className="error-text" role="alert" initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>{error}</motion.div>}
          </AnimatePresence>

          <button className="btn btn-primary btn-lg" disabled={busy}>
            {busy ? <span className="spinner" /> : <>{isRegister ? 'Create account' : 'Sign in'} <ArrowRight size={17} /></>}
          </button>
          <p className="muted small" style={{ textAlign: 'center' }}>
            {isRegister ? 'Already have an account? ' : 'New here? '}
            <Link to={isRegister ? '/login' : '/register'} state={location.state} style={{ fontWeight: 600 }}>{isRegister ? 'Sign in' : 'Create an account'}</Link>
          </p>
        </motion.form>
      </div>
    </div>
  );
}
