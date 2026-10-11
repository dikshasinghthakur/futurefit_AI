import { useEffect, useState } from 'react';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { ExternalLink, GraduationCap, Search } from 'lucide-react';
import { api } from '../lib/api.js';
import { fadeUp, stagger } from '../lib/motion.js';
import EmptyState from '../components/EmptyState.jsx';
import Segmented from '../components/Segmented.jsx';
import { CardSkeleton } from '../components/Skeleton.jsx';

function useDebounced(value, ms = 300) {
  const [v, setV] = useState(value);
  useEffect(() => { const t = setTimeout(() => setV(value), ms); return () => clearTimeout(t); }, [value, ms]);
  return v;
}

export default function Courses() {
  const [q, setQ] = useState('');
  const [level, setLevel] = useState('');
  const [page, setPage] = useState(1);
  const [curated, setCurated] = useState(true);
  const dq = useDebounced(q);

  useEffect(() => { setPage(1); }, [dq, level, curated]);

  const params = new URLSearchParams({ page, page_size: 12 });
  if (dq) params.set('q', dq);
  if (level) params.set('level', level);
  if (curated) params.set('curated', 'true');

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['courses', params.toString()], queryFn: () => api.get(`/courses?${params}`), placeholderData: keepPreviousData,
  });

  return (
    <>
      <div className="page-head"><div><h1>Learning resources</h1><p className="muted">Hand-picked courses and docs, mapped to the skills they teach.</p></div></div>

      <div className="row wrap">
        <div style={{ position: 'relative', flex: '1 1 260px' }}>
          <Search size={16} className="muted" style={{ position: 'absolute', left: 13, top: 14 }} />
          <input className="input" style={{ paddingLeft: 38 }} placeholder="Search courses…" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Search courses" />
        </div>
        <Segmented label="Level" value={level} onChange={setLevel} options={[{ value: '', label: 'All' }, { value: 'beginner', label: 'Beginner' }, { value: 'intermediate', label: 'Intermediate' }]} />
        <Segmented label="Source" value={curated} onChange={setCurated} options={[{ value: true, label: 'Curated' }, { value: false, label: 'Include search links' }]} />
      </div>

      {isLoading && <div className="grid g3">{[0, 1, 2, 3, 4, 5].map((i) => <CardSkeleton key={i} lines={2} h={40} />)}</div>}
      {data?.items.length === 0 && <EmptyState icon={GraduationCap} title="No courses match" text="Try a different search or clear the filters." />}

      <motion.div variants={stagger(0.04)} initial="hidden" animate="show" key={page + (dq || '') + level + curated} className="grid g3" style={{ opacity: isFetching ? 0.7 : 1, transition: 'opacity .2s' }}>
        {data?.items.map((c) => (
          <motion.a key={c.id} variants={fadeUp} href={c.url} target="_blank" rel="noopener noreferrer" className="card interactive col" style={{ gap: 10 }}>
            <div className="row between"><span className="chip accent">{c.level}</span>{c.free && <span className="chip ok">free</span>}</div>
            <h3>{c.title}</h3>
            <div className="muted small">{c.provider} · ~{c.hours}h</div>
            <div className="chips">{c.skills.map((s) => <span key={s.slug} className="chip">{s.name}</span>)}</div>
            <span className="small" style={{ fontWeight: 600, marginTop: 'auto' }}>Open <ExternalLink size={13} style={{ verticalAlign: -2 }} /></span>
          </motion.a>
        ))}
      </motion.div>

      {data && data.pages > 1 && (
        <div className="row" style={{ justifyContent: 'center' }}>
          <button className="btn btn-ghost" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Previous</button>
          <span className="muted small">Page {data.page} of {data.pages}</span>
          <button className="btn btn-ghost" disabled={page >= data.pages} onClick={() => setPage((p) => p + 1)}>Next</button>
        </div>
      )}
    </>
  );
}
