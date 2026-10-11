import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Bar, Doughnut, Line, Radar } from 'react-chartjs-2';
import { ArrowRight, CheckCheck, Clock, Compass, FileUp, Gauge, Target, TrendingUp } from 'lucide-react';
import { api } from '../lib/api.js';
import { useAuth } from '../lib/auth.jsx';
import { alpha, tooltipStyle, useChartColors } from '../lib/charts.js';
import { firstName, plural, shortDate } from '../lib/format.js';
import { fadeUp, stagger } from '../lib/motion.js';
import AnimatedNumber from '../components/AnimatedNumber.jsx';
import { CardSkeleton } from '../components/Skeleton.jsx';
import ScoreRing from '../components/ScoreRing.jsx';

function Stat({ icon: Icon, label, value, suffix = '', decimals = 0, empty = '—' }) {
  return (
    <motion.div variants={fadeUp} className="card stat" whileHover={{ y: -3 }}>
      <div className="stat-icon"><Icon size={19} /></div>
      <div className="stat-value">{value == null ? empty : <AnimatedNumber value={value} suffix={suffix} decimals={decimals} />}</div>
      <div className="muted small">{label}</div>
    </motion.div>
  );
}

function Charts({ data }) {
  const c = useChartColors();
  const la = data.latest_analysis;
  const grid = { color: alpha(c.grid, 0.9) };
  const catLabels = la ? Object.keys(la.category_breakdown) : [];
  const trend = data.readiness_trend;
  const act = data.activity;
  const cats = Object.entries(data.skills_by_category);
  const palette = [c.accent, c.accent2, '#ec4899', c.ok, c.warn, '#06b6d4', '#f97316', '#84cc16'];

  return (
    <>
      <div className="grid g2">
        <div className="card">
          <div className="card-title"><h2>Strengths by category</h2><span className="muted small">{la?.role_title}</span></div>
          <div className="chart-box">
            {catLabels.length >= 3 ? (
              <Radar data={{ labels: catLabels, datasets: [{ data: catLabels.map((k) => la.category_breakdown[k].score), backgroundColor: alpha(c.accent, 0.18), borderColor: c.accent, borderWidth: 2, pointBackgroundColor: c.accent }] }}
                options={{ scales: { r: { min: 0, max: 100, ticks: { display: false, stepSize: 25 }, grid, angleLines: grid, pointLabels: { color: c.text, font: { size: 11 } } } }, plugins: { tooltip: { ...tooltipStyle(c), callbacks: { label: (x) => `${x.raw}% covered` } } } }} />
            ) : <Bar data={{ labels: catLabels, datasets: [{ data: catLabels.map((k) => la?.category_breakdown[k].score), backgroundColor: c.accent, borderRadius: 8 }] }} options={{ scales: { y: { min: 0, max: 100, grid }, x: { grid: { display: false } } } }} />}
          </div>
        </div>
        <div className="card">
          <div className="card-title"><h2>Readiness over time</h2><span className="muted small">{plural(trend.length, 'analysis', 'analyses')}</span></div>
          <div className="chart-box">
            <Line data={{ labels: trend.map((t) => shortDate(t.date)), datasets: [{ data: trend.map((t) => t.score), borderColor: c.accent, backgroundColor: alpha(c.accent, 0.14), fill: true, tension: 0.35, borderWidth: 3, pointRadius: 4, pointBackgroundColor: c.card, pointBorderColor: c.accent, pointBorderWidth: 2 }] }}
              options={{ scales: { y: { min: 0, max: 100, grid, ticks: { color: c.text, callback: (v) => `${v}%` } }, x: { grid: { display: false }, ticks: { color: c.text } } }, plugins: { tooltip: { ...tooltipStyle(c), callbacks: { label: (x) => `${x.raw}% · ${trend[x.dataIndex].role_title}` } } } }} />
          </div>
        </div>
      </div>
      <div className="grid g-main">
        <div className="card">
          <div className="card-title"><h2>Learning activity</h2><span className="muted small">Last 30 days</span></div>
          <div className="chart-box" style={{ height: 220 }}>
            <Bar data={{ labels: act.map((a) => shortDate(a.date)), datasets: [{ data: act.map((a) => a.count), backgroundColor: alpha(c.accent, 0.85), borderRadius: 6, maxBarThickness: 16 }] }}
              options={{ scales: { y: { beginAtZero: true, grid, ticks: { stepSize: 1, precision: 0, color: c.text } }, x: { grid: { display: false }, ticks: { color: c.text, maxTicksLimit: 6, maxRotation: 0 } } }, plugins: { tooltip: { ...tooltipStyle(c), callbacks: { label: (x) => plural(x.raw, 'step') + ' completed' } } } }} />
          </div>
        </div>
        <div className="card">
          <div className="card-title"><h2>Your skills</h2><span className="muted small">From latest resume</span></div>
          {cats.length ? (
            <div className="chart-box" style={{ height: 220 }}>
              <Doughnut data={{ labels: cats.map(([k]) => k), datasets: [{ data: cats.map(([, v]) => v), backgroundColor: cats.map((_, i) => palette[i % palette.length]), borderColor: c.card, borderWidth: 3 }] }}
                options={{ cutout: '66%', plugins: { legend: { display: true, position: 'right', labels: { color: c.text, boxWidth: 10, boxHeight: 10, usePointStyle: true, font: { size: 11 } } }, tooltip: tooltipStyle(c) } }} />
            </div>
          ) : <p className="muted">Upload a resume to see your skill mix.</p>}
        </div>
      </div>
    </>
  );
}

export default function Dashboard() {
  const { user } = useAuth();
  const { data, isLoading, error } = useQuery({ queryKey: ['dashboard'], queryFn: () => api.get('/dashboard') });

  if (isLoading) return (<><div className="col"><div className="skeleton" style={{ height: 34, width: 280 }} /></div><div className="grid g4">{[0, 1, 2, 3].map((i) => <CardSkeleton key={i} lines={1} h={60} />)}</div><div className="grid g2"><CardSkeleton h={220} /><CardSkeleton h={220} /></div></>);
  if (error) return <div className="card"><h2>Couldn't load your dashboard</h2><p className="muted">{error.message}</p></div>;

  const { stats, latest_analysis: la, active_roadmap: rm } = data;

  if (!la) {
    return (
      <>
        <div className="page-head"><div><h1>Welcome, {firstName(user?.name)} 👋</h1><p className="muted">Let's find out where you stand — it takes about a minute.</p></div></div>
        <motion.div variants={stagger(0.1)} initial="hidden" animate="show" className="grid g3">
          {[{ n: 1, icon: FileUp, t: 'Upload your resume', d: 'PDF, DOCX or pasted text. We extract your skills automatically.' },
            { n: 2, icon: Target, t: 'Pick a target role', d: 'See how your skills stack up against what the role demands.' },
            { n: 3, icon: Compass, t: 'Follow your roadmap', d: 'A prerequisite-aware plan with courses matched to every gap.' }].map(({ n, icon: Icon, t, d }) => (
            <motion.div key={n} variants={fadeUp} className="card col"><div className="stat-icon"><Icon size={19} /></div><h3>{n}. {t}</h3><p className="muted small">{d}</p></motion.div>
          ))}
        </motion.div>
        <div><Link to="/resume" className="btn btn-primary btn-lg"><FileUp size={18} /> Upload resume <ArrowRight size={17} /></Link></div>
      </>
    );
  }

  return (
    <>
      <div className="page-head">
        <div><h1>Welcome back, {firstName(user?.name)}</h1><p className="muted">Here's how your career readiness is shaping up.</p></div>
        <Link to="/resume" className="btn btn-primary"><FileUp size={17} /> New analysis</Link>
      </div>

      <motion.div variants={stagger(0.07)} initial="hidden" animate="show" className="grid g4">
        <Stat icon={Gauge} label="Role readiness" value={stats.readiness} suffix="%" decimals={0} />
        <Stat icon={TrendingUp} label="Roadmap progress" value={stats.roadmap_progress} suffix="%" decimals={0} empty="No roadmap" />
        <Stat icon={CheckCheck} label="Steps completed" value={stats.completed_items} />
        <Stat icon={Clock} label="Hours learned" value={stats.hours_learned} />
      </motion.div>

      <div className="grid g-main">
        <motion.div className="card row wrap" style={{ gap: 28 }} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <ScoreRing value={la.readiness_score} size={168} label={la.readiness_label} />
          <div className="col grow" style={{ minWidth: 220 }}>
            <div><div className="muted small">Latest analysis</div><h2 style={{ fontSize: '1.3rem' }}>{la.role_title}</h2></div>
            <div className="chips"><span className="chip ok">{la.counts.matched} matched</span><span className="chip warn">{la.counts.partial} partial</span><span className="chip bad">{la.counts.missing} missing</span></div>
            <p className="muted small">{la.summary}</p>
            <div><Link to={`/analysis/${la.id}`} className="btn btn-ghost">View breakdown <ArrowRight size={16} /></Link></div>
          </div>
        </motion.div>

        <motion.div className="card col" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.28 }}>
          <div className="card-title" style={{ marginBottom: 0 }}><h2>Up next</h2>{rm && <Link to={`/roadmap/${rm.id}`} className="small" style={{ fontWeight: 600 }}>Open roadmap</Link>}</div>
          {rm ? (
            <>
              <div><div className="row between small"><span className="muted">{rm.role_title}</span><b>{Math.round(rm.progress_pct)}%</b></div>
                <div className="bar" style={{ marginTop: 6 }}><motion.div initial={{ width: 0 }} animate={{ width: `${rm.progress_pct}%` }} transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }} /></div></div>
              {rm.next_items.length ? rm.next_items.map((it) => (
                <Link key={it.id} to={`/roadmap/${rm.id}`} className="row between item" style={{ padding: '10px 12px', color: 'inherit' }}>
                  <span style={{ fontWeight: 600 }}>{it.skill_name}</span><span className="chip">{it.est_hours}h</span>
                </Link>
              )) : <p className="muted small">Everything's done — nice work! Re-analyse your resume to see your new score.</p>}
            </>
          ) : (
            <><p className="muted small">You haven't generated a roadmap yet. Turn your gaps into a step-by-step plan.</p>
              <Link to={`/analysis/${la.id}`} className="btn btn-primary"><Compass size={16} /> Build my roadmap</Link></>
          )}
        </motion.div>
      </div>

      <Charts data={data} />
    </>
  );
}
