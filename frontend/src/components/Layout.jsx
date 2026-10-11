import { useEffect, useState } from 'react';
import { Link, NavLink, useLocation, useNavigate, useOutlet } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { Compass, FileText, GraduationCap, LayoutDashboard, LogOut, Menu, Target, User, X } from 'lucide-react';
import { useAuth } from '../lib/auth';
import { initials } from '../lib/format';
import { pageVariants, spring } from '../lib/motion';
import ThemeToggle from './ThemeToggle';

const NAV = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/resume', label: 'Resume', icon: FileText },
  { to: '/analysis', label: 'Skill gap', icon: Target },
  { to: '/roadmap', label: 'Roadmap', icon: Compass },
  { to: '/courses', label: 'Courses', icon: GraduationCap },
  { to: '/profile', label: 'Profile', icon: User },
];

function Brand() {
  return (
    <Link to="/dashboard" className="brand" style={{ color: 'inherit' }}>
      <span className="brand-mark"><Target size={18} /></span>FutureFit <span className="gradient-text">AI</span>
    </Link>
  );
}

function SidebarContent({ onNavigate }) {
  const { user, logout } = useAuth();
  const { pathname } = useLocation();
  const navigate = useNavigate();
  return (
    <>
      <Brand />
      <nav className="col" style={{ gap: 4 }} aria-label="Main">
        {NAV.map(({ to, label, icon: Icon }) => {
          const active = pathname === to || pathname.startsWith(`${to}/`);
          return (
            <NavLink key={to} to={to} onClick={onNavigate} className={`nav-link${active ? ' active' : ''}`}>
              {active && <motion.span layoutId="nav-pill" className="nav-pill" transition={spring} />}
              <Icon size={19} /> <span>{label}</span>
            </NavLink>
          );
        })}
      </nav>
      <div className="sidebar-foot">
        <div className="user-box">
          <div className="avatar">{initials(user?.name)}</div>
          <div className="grow"><div style={{ fontWeight: 650, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{user?.name}</div>
            <div className="muted tiny" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{user?.email}</div></div>
        </div>
        <div className="row">
          <ThemeToggle />
          <button className="btn btn-ghost grow" onClick={() => { logout(); navigate('/'); }}><LogOut size={16} /> Sign out</button>
        </div>
      </div>
    </>
  );
}

export default function Layout() {
  const location = useLocation();
  const outlet = useOutlet(); // captured per-render so the exiting page keeps its own content during the transition
  const [open, setOpen] = useState(false);

  useEffect(() => { window.scrollTo({ top: 0 }); setOpen(false); }, [location.pathname]);

  return (
    <div className="shell">
      <aside className="sidebar desktop"><SidebarContent /></aside>

      <header className="mobile-bar">
        <Brand />
        <button className="btn btn-ghost btn-icon" onClick={() => setOpen(true)} aria-label="Open menu"><Menu size={20} /></button>
      </header>
      <AnimatePresence>
        {open && (
          <>
            <motion.div className="scrim" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setOpen(false)} />
            <motion.aside className="sidebar drawer" initial={{ x: '-100%' }} animate={{ x: 0 }} exit={{ x: '-100%' }} transition={{ type: 'spring', stiffness: 380, damping: 36 }}>
              <button className="btn btn-ghost btn-icon" style={{ position: 'absolute', right: 12, top: 14 }} onClick={() => setOpen(false)} aria-label="Close menu"><X size={18} /></button>
              <SidebarContent onNavigate={() => setOpen(false)} />
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      <main className="main">
        <AnimatePresence mode="wait" initial={false}>
          <motion.div key={location.pathname} className="page" variants={pageVariants} initial="initial" animate="enter" exit="exit">
            {outlet}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
