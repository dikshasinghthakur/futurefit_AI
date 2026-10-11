import { Link, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { AnimatePresence, motion } from 'framer-motion';
import { ArrowLeft, Check, Clock, ExternalLink, PartyPopper, RefreshCw, Trophy } from 'lucide-react';
import { api } from '../lib/api.js';
import { fadeUp, stagger } from '../lib/motion.js';
import { CardSkeleton } from '../components/Skeleton.jsx';
import AnimatedNumber from '../components/AnimatedNumber.jsx';
import { useToast } from '../components/Toast.jsx';

const progressOf = (phases) => {
  const items = phases.flatMap((p) => p.items);
  const total = items.reduce((s, i) => s + i.est_hours, 0) || 1;
  const done = items.filter((i) => i.completed);
  const doneH = done.reduce((s, i) => s + i.est_hours, 0);
  return { progress_pct: Math.round((1000 * doneH) / total) / 10, completed_hours: doneH, completed_items: done.length, total_items: items.length };
};

export default function RoadmapDetail() {
  const { id } = useParams();
  const qc = useQueryClient();
  const toast = useToast();
  const key = ['roadmap', id];
  const { data: rm, isLoading, error } = useQuery({ queryKey: key, queryFn: () => api.get(`/roadmaps/${id}`) });

  // Optimistic toggle: the UI responds instantly; roll back if the server rejects it.
  const toggle = useMutation({
    mutationFn: ({ itemId, completed }) => api.patch(`/roadmaps/${id}/items/${itemId}`, { completed }),
    onMutate: async ({ itemId, completed }) => {
      await qc.cancelQueries({ queryKey: key });
      const prev = qc.getQueryData(key);
      qc.setQueryData(key, (old) => {
        const phases = old.phases.map((p) => ({ ...p, items: p.items.map((i) => (i.id === itemId ? { ...i, completed } : i)) }));
        return { ...old, phases, ...progressOf(phases) };
      });
      return { prev };
    },
    onError: (e, _v, ctx) => { qc.setQueryData(key, ctx.prev); toast.error(e.message); },
    onSuccess: (data, v) => {
      if (v.completed && data.progress_pct >= 100) toast.success('Roadmap complete! Re-analyse your resume to see your new score.');
    },
    onSettled: () => { qc.invalidateQueries({ queryKey: ['dashboard'] }); qc.invalidateQueries({ queryKey: ['roadmaps'] }); },
  });

  if (isLoading) return <><CardSkeleton h={80} /><CardSkeleton h={160} /></>;
  if (error) return <div className="card"><h2>Roadmap not found</h2><p className="muted">{error.message}</p></div>;

  const complete = rm.progress_pct >= 100;

  return (
    <>
      <div><Link to="/roadmap" className="small row" style={{ gap: 6, fontWeight: 600 }}><ArrowLeft size={15} /> All roadmaps</Link></div>

      <div className="card col" style={{ gap: 16 }}>
        <div className="row between wrap">
          <div><div className="muted small">Roadmap for</div><h1>{rm.role_title}</h1></div>
          <div className="stat-value gradient-text"><AnimatedNumber value={rm.progress_pct} decimals={0} suffix="%" /></div>
        </div>
        <div className="bar" style={{ height: 12 }}>
          <motion.div animate={{ width: `${rm.progress_pct}%` }} initial={false} transition={{ type: 'spring', stiffness: 120, damping: 20 }} style={complete ? { background: 'var(--ok)' } : undefined} />
        </div>
        <div className="chips">
          <span className="chip"><Check size={12} /> {rm.completed_items}/{rm.total_items} steps</span>
          <span className="chip"><Clock size={12} /> {rm.completed_hours}/{rm.total_hours} hours</span>
          <span className="chip">~{rm.estimated_weeks} weeks at {rm.hours_per_week}h/week</span>
          <span className="chip accent">Started at {Math.round(rm.start_readiness)}% readiness</span>
        </div>
        <AnimatePresence>
          {rm.completed_items > 0 && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} style={{ overflow: 'hidden' }}>
              <div className="item project" style={{ alignItems: 'center' }}>
                {complete ? <Trophy size={18} color="var(--accent)" /> : <RefreshCw size={18} color="var(--accent)" />}
                <span className="small grow">Completed skills count toward your next analysis — run it again on your <Link to="/resume" style={{ fontWeight: 600 }}>resume</Link> to see your score move.</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <motion.div variants={stagger(0.1)} initial="hidden" animate="show" className="timeline">
        {rm.phases.map((ph) => {
          const done = ph.items.every((i) => i.completed);
          return (
            <motion.section key={ph.index} variants={fadeUp} className="phase">
              <div className={`phase-node${done ? ' done' : ''}`}>{done ? <Check size={13} /> : ph.index}</div>
              <div className="row between wrap" style={{ marginBottom: 12 }}>
                <div><h2>{ph.title} <span className="muted" style={{ fontWeight: 500 }}>· {ph.weeks}</span></h2><div className="muted small">Focus: {ph.focus}</div></div>
                <span className="chip">{ph.hours}h</span>
              </div>
              <div className="col" style={{ gap: 10 }}>
                {ph.items.map((it) => (
                  <motion.div layout key={it.id} className={`item${it.completed ? ' done' : ''}${it.type === 'project' ? ' project' : ''}`}>
                    <button className={`check${it.completed ? ' on' : ''}`} role="checkbox" aria-checked={it.completed}
                      aria-label={`Mark ${it.skill_name} ${it.completed ? 'incomplete' : 'complete'}`}
                      onClick={() => toggle.mutate({ itemId: it.id, completed: !it.completed })}>
                      <AnimatePresence initial={false}>
                        {it.completed && <motion.span key="c" style={{ display: 'grid' }} initial={{ scale: 0, rotate: -40 }} animate={{ scale: 1, rotate: 0 }} exit={{ scale: 0 }} transition={{ type: 'spring', stiffness: 500, damping: 22 }}><Check size={16} strokeWidth={3} /></motion.span>}
                      </AnimatePresence>
                    </button>
                    <div className="grow">
                      <div className="row between wrap" style={{ gap: 8 }}>
                        <b className={it.completed ? 'strike' : ''}>{it.type === 'project' && <PartyPopper size={15} style={{ verticalAlign: -2, marginRight: 6 }} />}{it.skill_name}</b>
                        <div className="chips"><span className="chip">{it.est_hours}h</span>{it.status === 'partial' && <span className="chip warn">partial</span>}</div>
                      </div>
                      <p className="muted small" style={{ marginTop: 2 }}>{it.reason}</p>
                      {it.course && (
                        <a className="course" href={it.course.url} target="_blank" rel="noopener noreferrer">
                          <span><b className="small">{it.course.title}</b><br /><span className="muted tiny">{it.course.provider} · {it.course.level}{it.course.free ? ' · free' : ''}</span></span>
                          <ExternalLink size={15} />
                        </a>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.section>
          );
        })}
      </motion.div>
    </>
  );
}
