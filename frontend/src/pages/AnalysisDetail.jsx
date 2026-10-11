import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { ArrowLeft, Compass, Sparkles } from 'lucide-react';
import { api } from '../lib/api.js';
import { fmtDate } from '../lib/format.js';
import { fadeUp, stagger } from '../lib/motion.js';
import Importance from '../components/Importance.jsx';
import ScoreRing from '../components/ScoreRing.jsx';
import Segmented from '../components/Segmented.jsx';
import { CardSkeleton } from '../components/Skeleton.jsx';
import { useToast } from '../components/Toast.jsx';

const COLUMNS = [
  { key: 'matched', title: 'Matched', chip: 'ok', note: 'You already have these' },
  { key: 'partial', title: 'Partial', chip: 'warn', note: 'Related knowledge — build on it' },
  { key: 'missing', title: 'Missing', chip: 'bad', note: 'Learn these next' },
];

export default function AnalysisDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const qc = useQueryClient();
  const [hours, setHours] = useState(8);
  const { data: a, isLoading, error } = useQuery({ queryKey: ['analysis', id], queryFn: () => api.get(`/analyses/${id}`) });

  const build = useMutation({
    mutationFn: () => api.post('/roadmaps', { analysis_id: id, hours_per_week: hours }),
    onSuccess: (r) => { qc.invalidateQueries({ queryKey: ['roadmaps'] }); qc.invalidateQueries({ queryKey: ['dashboard'] }); navigate(`/roadmap/${r.id}`); },
    onError: (e) => toast.error(e.message),
  });

  if (isLoading) return <><CardSkeleton h={160} /><div className="grid g3"><CardSkeleton /><CardSkeleton /><CardSkeleton /></div></>;
  if (error) return <div className="card"><h2>Analysis not found</h2><p className="muted">{error.message}</p><Link to="/analysis" className="btn btn-ghost" style={{ marginTop: 12 }}>Back</Link></div>;

  const cats = Object.entries(a.category_breakdown).sort((x, y) => y[1].score - x[1].score);

  return (
    <>
      <div><Link to="/analysis" className="small row" style={{ gap: 6, fontWeight: 600 }}><ArrowLeft size={15} /> All analyses</Link></div>

      <motion.div className="card row wrap" style={{ gap: 32 }} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
        <ScoreRing value={a.readiness_score} size={190} label={a.readiness_label} sublabel="role readiness" />
        <div className="col grow" style={{ minWidth: 240 }}>
          <div><div className="muted small">{fmtDate(a.created_at)} · {a.resume_title}</div><h1>{a.role_title}</h1></div>
          <div className="chips"><span className="chip ok">{a.counts.matched} matched</span><span className="chip warn">{a.counts.partial} partial</span><span className="chip bad">{a.counts.missing} missing</span></div>
          <p>{a.summary}</p>
          {a.coach_note && <div className="item project" style={{ alignItems: 'center' }}><Sparkles size={18} color="var(--accent)" style={{ flex: 'none' }} /><span className="small">{a.coach_note}</span></div>}
          {a.acquired_skills?.length > 0 && <p className="muted small">Includes {a.acquired_skills.length} skill(s) you completed on your roadmap.</p>}
        </div>
      </motion.div>

      <div className="card col">
        <h2>Coverage by category</h2>
        {cats.map(([name, v], i) => (
          <div key={name}>
            <div className="row between small"><span style={{ fontWeight: 600 }}>{name}</span><span className="muted">{Math.round(v.score)}%</span></div>
            <div className={`bar ${v.score >= 70 ? 'ok' : v.score >= 35 ? 'warn' : ''}`} style={{ marginTop: 5 }}>
              <motion.div initial={{ width: 0 }} animate={{ width: `${v.score}%` }} transition={{ duration: 0.9, delay: 0.1 + i * 0.07, ease: [0.22, 1, 0.36, 1] }} style={v.score < 35 ? { background: 'var(--bad)' } : undefined} />
            </div>
          </div>
        ))}
      </div>

      <div className="grid g3" style={{ alignItems: 'start' }}>
        {COLUMNS.map((col) => (
          <div key={col.key} className="card col">
            <div><div className="row between"><h2>{col.title}</h2><span className={`chip ${col.chip}`}>{a[col.key].length}</span></div><p className="muted tiny">{col.note}</p></div>
            <motion.div variants={stagger(0.04)} initial="hidden" animate="show" className="col" style={{ gap: 8 }}>
              {a[col.key].length === 0 && <p className="muted small">Nothing here.</p>}
              {a[col.key].map((s) => (
                <motion.div key={s.skill} variants={fadeUp} className="item" style={{ padding: 12, flexDirection: 'column', gap: 4 }}>
                  <div className="row between" style={{ width: '100%' }}><b>{s.name}</b><Importance weight={s.weight} /></div>
                  <div className="muted tiny">
                    {s.status === 'matched' && s.via_name && `Covered via ${s.via_name}`}
                    {s.status === 'matched' && !s.via_name && s.category}
                    {s.status === 'partial' && `Builds on ${s.via_name}`}
                    {s.status === 'missing' && (s.alternatives.length ? `Or: ${s.alternatives.join(', ')}` : s.category)}
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        ))}
      </div>

      <div className="card row wrap between" style={{ gap: 18, background: 'linear-gradient(135deg, var(--accent-soft), var(--bg-elev))' }}>
        <div><h2>Turn this into a plan</h2><p className="muted small">How many hours per week can you commit?</p></div>
        <div className="row wrap">
          <Segmented label="Hours per week" value={hours} onChange={setHours} options={[4, 8, 12, 20].map((h) => ({ value: h, label: `${h}h` }))} />
          <button className="btn btn-primary" disabled={build.isPending || (a.counts.missing + a.counts.partial === 0)} onClick={() => build.mutate()}>
            {build.isPending ? <span className="spinner" /> : <><Compass size={16} /> Build my roadmap</>}
          </button>
        </div>
      </div>
    </>
  );
}
