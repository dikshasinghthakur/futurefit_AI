import { useEffect, useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Save } from 'lucide-react';
import { api } from '../lib/api.js';
import { useAuth } from '../lib/auth.jsx';
import { useToast } from '../components/Toast.jsx';

const EMPTY = { headline: '', education: '', graduation_year: '', location: '', career_goal: '', target_role_slug: '' };

export default function Profile() {
  const { user, setUser } = useAuth();
  const toast = useToast();
  const { data: roles } = useQuery({ queryKey: ['roles'], queryFn: () => api.get('/roles'), staleTime: 10 * 60_000 });
  const [form, setForm] = useState(EMPTY);

  useEffect(() => { setForm({ ...EMPTY, ...Object.fromEntries(Object.entries(user?.profile || {}).map(([k, v]) => [k, v ?? ''])) }); }, [user]);

  const save = useMutation({
    mutationFn: () => api.put('/profile', {
      ...form, graduation_year: form.graduation_year ? Number(form.graduation_year) : null,
      ...Object.fromEntries(['headline', 'education', 'location', 'career_goal', 'target_role_slug'].map((k) => [k, form[k] || null])),
    }),
    onSuccess: (u) => { setUser(u); toast.success('Profile saved'); },
    onError: (e) => toast.error(e.message),
  });
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  return (
    <>
      <div className="page-head"><div><h1>Your profile</h1><p className="muted">Used to pre-select your target role and personalise your dashboard.</p></div></div>
      <form className="card col" style={{ maxWidth: 720, gap: 18 }} onSubmit={(e) => { e.preventDefault(); save.mutate(); }}>
        <div className="grid g2">
          <div className="field"><label>Name</label><input className="input" value={user?.name || ''} readOnly /></div>
          <div className="field"><label>Email</label><input className="input" value={user?.email || ''} readOnly /></div>
        </div>
        <div className="field"><label htmlFor="headline">Headline</label><input id="headline" className="input" maxLength={120} placeholder="e.g. Final-year CSE student" value={form.headline} onChange={set('headline')} /></div>
        <div className="grid g2">
          <div className="field"><label htmlFor="edu">Education</label><input id="edu" className="input" maxLength={160} placeholder="B.Tech CSE, Echelon Institute" value={form.education} onChange={set('education')} /></div>
          <div className="field"><label htmlFor="grad">Graduation year</label><input id="grad" type="number" min="1990" max="2100" className="input" value={form.graduation_year} onChange={set('graduation_year')} /></div>
        </div>
        <div className="grid g2">
          <div className="field"><label htmlFor="loc">Location</label><input id="loc" className="input" maxLength={80} value={form.location} onChange={set('location')} /></div>
          <div className="field"><label htmlFor="role">Target role</label>
            <select id="role" className="select" value={form.target_role_slug} onChange={set('target_role_slug')}><option value="">Not set</option>{roles?.map((r) => <option key={r.slug} value={r.slug}>{r.title}</option>)}</select></div>
        </div>
        <div className="field"><label htmlFor="goal">Career goal</label><textarea id="goal" className="textarea" maxLength={500} placeholder="What do you want to be doing in two years?" value={form.career_goal} onChange={set('career_goal')} /></div>
        <div><button className="btn btn-primary" disabled={save.isPending}>{save.isPending ? <span className="spinner" /> : <><Save size={16} /> Save changes</>}</button></div>
      </form>
    </>
  );
}
