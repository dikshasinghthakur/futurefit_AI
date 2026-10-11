import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { ArrowRight, FileUp, Target } from 'lucide-react';
import { api } from '../lib/api.js';
import { fmtDate } from '../lib/format.js';
import { fadeUp, stagger } from '../lib/motion.js';
import EmptyState from '../components/EmptyState.jsx';
import ScoreRing from '../components/ScoreRing.jsx';
import { CardSkeleton } from '../components/Skeleton.jsx';

export default function Analysis() {
  const { data, isLoading } = useQuery({ queryKey: ['analyses'], queryFn: () => api.get('/analyses?page_size=50') });

  return (
    <>
      <div className="page-head"><div><h1>Skill gap analyses</h1><p className="muted">Every analysis is saved so you can watch your readiness improve.</p></div>
        <Link to="/resume" className="btn btn-primary"><FileUp size={16} /> New analysis</Link></div>
      {isLoading && <div className="grid g3">{[0, 1, 2].map((i) => <CardSkeleton key={i} />)}</div>}
      {data?.items.length === 0 && <EmptyState icon={Target} title="No analyses yet" text="Upload a resume and pick a target role to see your skill gap." action={<Link to="/resume" className="btn btn-primary">Upload resume</Link>} />}
      <motion.div variants={stagger(0.06)} initial="hidden" animate="show" className="grid g3">
        {data?.items.map((a) => (
          <motion.div key={a.id} variants={fadeUp}>
            <Link to={`/analysis/${a.id}`} className="card interactive col" style={{ alignItems: 'center', textAlign: 'center' }}>
              <ScoreRing value={a.readiness_score} size={120} stroke={11} />
              <div><h3>{a.role_title}</h3><div className="muted tiny">{fmtDate(a.created_at)}</div></div>
              <div className="chips" style={{ justifyContent: 'center' }}><span className="chip ok">{a.counts.matched}</span><span className="chip warn">{a.counts.partial}</span><span className="chip bad">{a.counts.missing}</span></div>
              <span className="small" style={{ fontWeight: 600 }}>View details <ArrowRight size={13} style={{ verticalAlign: -2 }} /></span>
            </Link>
          </motion.div>
        ))}
      </motion.div>
    </>
  );
}
