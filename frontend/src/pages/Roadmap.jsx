import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Clock, Compass, Target } from 'lucide-react';
import { api } from '../lib/api.js';
import { fmtDate } from '../lib/format.js';
import { fadeUp, stagger } from '../lib/motion.js';
import EmptyState from '../components/EmptyState.jsx';
import { CardSkeleton } from '../components/Skeleton.jsx';

export default function Roadmap() {
  const { data, isLoading } = useQuery({ queryKey: ['roadmaps'], queryFn: () => api.get('/roadmaps?page_size=50') });
  return (
    <>
      <div className="page-head"><div><h1>Learning roadmaps</h1><p className="muted">Step-by-step plans generated from your skill gaps.</p></div></div>
      {isLoading && <div className="grid g3">{[0, 1, 2].map((i) => <CardSkeleton key={i} lines={2} h={50} />)}</div>}
      {data?.items.length === 0 && <EmptyState icon={Compass} title="No roadmap yet" text="Run a skill gap analysis first, then build a roadmap from it." action={<Link to="/analysis" className="btn btn-primary"><Target size={16} /> Go to analyses</Link>} />}
      <motion.div variants={stagger(0.06)} initial="hidden" animate="show" className="grid g3">
        {data?.items.map((r) => (
          <motion.div key={r.id} variants={fadeUp}>
            <Link to={`/roadmap/${r.id}`} className="card interactive col">
              <div><h3>{r.role_title}</h3><div className="muted tiny">Created {fmtDate(r.created_at)}</div></div>
              <div><div className="row between small"><span className="muted">{r.completed_items}/{r.total_items} steps</span><b>{Math.round(r.progress_pct)}%</b></div>
                <div className="bar" style={{ marginTop: 6 }}><motion.div initial={{ width: 0 }} animate={{ width: `${r.progress_pct}%` }} transition={{ duration: 0.9 }} /></div></div>
              <div className="chips"><span className="chip"><Clock size={12} /> ~{r.estimated_weeks} weeks</span><span className="chip">{r.hours_per_week}h/week</span></div>
            </Link>
          </motion.div>
        ))}
      </motion.div>
    </>
  );
}
