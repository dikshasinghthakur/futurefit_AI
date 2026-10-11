import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { AnimatePresence, motion } from 'framer-motion';
import { ArrowRight, FileText, FileUp, Mail, Trash2, UploadCloud } from 'lucide-react';
import { api } from '../lib/api.js';
import { fmtDate, plural } from '../lib/format.js';
import { fadeUp, pop, stagger } from '../lib/motion.js';
import { useToast } from '../components/Toast.jsx';
import { useAuth } from '../lib/auth.jsx';
import Segmented from '../components/Segmented.jsx';
import { Skeleton } from '../components/Skeleton.jsx';

function Parsed({ resume }) {
  const { user } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { data: roles } = useQuery({ queryKey: ['roles'], queryFn: () => api.get('/roles'), staleTime: 10 * 60_000 });
  const [role, setRole] = useState(user?.profile?.target_role_slug || '');
  const p = resume.parsed;

  const groups = p.skills.reduce((acc, s) => { (acc[s.category] ||= []).push(s); return acc; }, {});
  const analyze = useMutation({
    mutationFn: () => api.post('/analyses', { resume_id: resume.id, role_slug: role }),
    onSuccess: (a) => { qc.invalidateQueries({ queryKey: ['dashboard'] }); qc.invalidateQueries({ queryKey: ['analyses'] }); navigate(`/analysis/${a.id}`); },
    onError: (e) => toast.error(e.message),
  });

  return (
    <motion.div key={resume.id} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="col" style={{ gap: 18 }}>
      <div className="card col">
        <div className="card-title" style={{ marginBottom: 0 }}><h2>{resume.title}</h2><span className="muted small">{fmtDate(resume.created_at)}</span></div>
        <div className="chips">
          <span className="chip accent">{plural(p.skills.length, 'skill')} found</span>
          {p.experience_years > 0 && <span className="chip">{p.experience_years} yrs experience</span>}
          {p.sections_found.map((s) => <span key={s} className="chip">{s}</span>)}
        </div>
        {p.contact.email && <div className="row muted small"><Mail size={14} /> {p.contact.email}</div>}
        {p.education.length > 0 && <div className="small"><b>Education</b><ul style={{ margin: '4px 0 0', paddingLeft: 18 }} className="muted">{p.education.map((e) => <li key={e}>{e}</li>)}</ul></div>}
        {p.certifications.length > 0 && <div className="small"><b>Certifications</b><ul style={{ margin: '4px 0 0', paddingLeft: 18 }} className="muted">{p.certifications.map((e) => <li key={e}>{e}</li>)}</ul></div>}
      </div>

      <div className="card col" style={{ gap: 16 }}>
        <h2>Skills we detected</h2>
        {p.skills.length === 0 && <p className="muted">We couldn't recognise any skills. Try adding a "Skills" section to your resume.</p>}
        {Object.entries(groups).map(([cat, list]) => (
          <div key={cat}>
            <div className="muted tiny" style={{ fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8 }}>{cat}</div>
            <motion.div variants={stagger(0.03)} initial="hidden" animate="show" className="chips">
              {list.map((s) => (
                <motion.span key={s.slug} variants={pop} className={`chip ${s.confidence >= 0.8 ? 'ok' : s.confidence >= 0.6 ? 'accent' : ''}`}
                  title={`Confidence ${Math.round(s.confidence * 100)}% · seen in ${s.evidence.join(', ')}`}>{s.name}</motion.span>
              ))}
            </motion.div>
          </div>
        ))}
        <p className="muted tiny">Colour shows confidence: green = listed and used in projects/experience.</p>
      </div>

      <div className="card col">
        <h2>Compare against a target role</h2>
        <div className="row wrap">
          <select className="select grow" value={role} onChange={(e) => setRole(e.target.value)} aria-label="Target role" style={{ minWidth: 220 }}>
            <option value="">Choose a role…</option>
            {roles?.map((r) => <option key={r.slug} value={r.slug}>{r.title}</option>)}
          </select>
          <button className="btn btn-primary" disabled={!role || analyze.isPending} onClick={() => analyze.mutate()}>
            {analyze.isPending ? <span className="spinner" /> : <>Analyse my gap <ArrowRight size={16} /></>}
          </button>
        </div>
      </div>
    </motion.div>
  );
}

export default function Resume() {
  const toast = useToast();
  const qc = useQueryClient();
  const fileRef = useRef(null);
  const [mode, setMode] = useState('file');
  const [drag, setDrag] = useState(false);
  const [text, setText] = useState('');
  const [selected, setSelected] = useState(null);

  const list = useQuery({ queryKey: ['resumes'], queryFn: () => api.get('/resumes?page_size=20') });
  const detail = useQuery({ queryKey: ['resume', selected], queryFn: () => api.get(`/resumes/${selected}`), enabled: !!selected });

  const onDone = (r) => {
    qc.setQueryData(['resume', r.id], r); setSelected(r.id); setText('');
    qc.invalidateQueries({ queryKey: ['resumes'] }); qc.invalidateQueries({ queryKey: ['dashboard'] });
    toast.success(`Found ${plural(r.parsed.skills.length, 'skill')} in your resume`);
  };
  const upload = useMutation({ mutationFn: (file) => { const f = new FormData(); f.append('file', file); return api.upload('/resumes', f); }, onSuccess: onDone, onError: (e) => toast.error(e.message) });
  const paste = useMutation({ mutationFn: () => api.post('/resumes/text', { text }), onSuccess: onDone, onError: (e) => toast.error(e.message) });
  const remove = useMutation({
    mutationFn: (id) => api.del(`/resumes/${id}`),
    onSuccess: (_, id) => { if (selected === id) setSelected(null); qc.invalidateQueries({ queryKey: ['resumes'] }); qc.invalidateQueries({ queryKey: ['dashboard'] }); toast.info('Resume deleted'); },
    onError: (e) => toast.error(e.message),
  });

  const busy = upload.isPending || paste.isPending;
  const pick = (file) => { if (file) upload.mutate(file); };

  return (
    <>
      <div className="page-head"><div><h1>Your resume</h1><p className="muted">Upload it once — we turn it into a structured skill profile.</p></div>
        <Segmented label="Input method" value={mode} onChange={setMode} options={[{ value: 'file', label: 'Upload file' }, { value: 'text', label: 'Paste text' }]} /></div>

      <div className="grid g-main" style={{ alignItems: 'start' }}>
        <div className="col" style={{ gap: 18 }}>
          <div className="card">
            <AnimatePresence mode="wait" initial={false}>
              {mode === 'file' ? (
                <motion.div key="file" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.18 }}>
                  <div className={`dropzone${drag ? ' drag' : ''}`} role="button" tabIndex={0} aria-label="Upload resume"
                    onClick={() => !busy && fileRef.current?.click()} onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && !busy && fileRef.current?.click()}
                    onDragOver={(e) => { e.preventDefault(); setDrag(true); }} onDragLeave={() => setDrag(false)}
                    onDrop={(e) => { e.preventDefault(); setDrag(false); if (!busy) pick(e.dataTransfer.files?.[0]); }}>
                    <input ref={fileRef} type="file" hidden accept=".pdf,.docx,.txt" onChange={(e) => { pick(e.target.files?.[0]); e.target.value = ''; }} />
                    <div className="dz-icon">{busy ? <span className="spinner" /> : <UploadCloud size={26} />}</div>
                    <div><b>{busy ? 'Reading your resume…' : 'Drop your resume here, or click to browse'}</b><div className="muted small">PDF, DOCX or TXT · up to 5 MB</div></div>
                    {busy && <div className="indeterminate" style={{ width: 'min(260px, 80%)' }} />}
                  </div>
                </motion.div>
              ) : (
                <motion.div key="text" className="col" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.18 }}>
                  <textarea className="textarea" style={{ minHeight: 220 }} placeholder="Paste your resume text here…" value={text} onChange={(e) => setText(e.target.value)} aria-label="Resume text" />
                  <div className="row between"><span className="muted tiny">{text.length.toLocaleString()} characters</span>
                    <button className="btn btn-primary" disabled={text.trim().length < 40 || busy} onClick={() => paste.mutate()}>{paste.isPending ? <span className="spinner" /> : <><FileUp size={16} /> Parse resume</>}</button></div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {selected && detail.isLoading && <div className="card col"><Skeleton h={22} w="40%" /><Skeleton h={14} /><Skeleton h={14} w="70%" /></div>}
          {selected && detail.data && <Parsed resume={detail.data} />}
        </div>

        <div className="card col">
          <div className="card-title" style={{ marginBottom: 0 }}><h2>Saved resumes</h2></div>
          {list.isLoading && <><Skeleton h={52} /><Skeleton h={52} /></>}
          {list.data?.items.length === 0 && <p className="muted small">Nothing here yet — your parsed resumes will appear here.</p>}
          <AnimatePresence initial={false}>
            {list.data?.items.map((r) => (
              <motion.div key={r.id} layout initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, height: 0, marginBottom: -12 }}
                className="item" style={{ cursor: 'pointer', alignItems: 'center', borderColor: selected === r.id ? 'var(--accent)' : undefined, padding: 12 }}
                onClick={() => setSelected(r.id)}>
                <div className="stat-icon"><FileText size={17} /></div>
                <div className="grow"><div style={{ fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{r.title}</div>
                  <div className="muted tiny">{plural(r.parsed.skills.length, 'skill')} · {fmtDate(r.created_at)}</div></div>
                <button className="btn btn-icon btn-ghost" aria-label={`Delete ${r.title}`} onClick={(e) => { e.stopPropagation(); if (window.confirm('Delete this resume?')) remove.mutate(r.id); }}><Trash2 size={15} /></button>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>
    </>
  );
}
