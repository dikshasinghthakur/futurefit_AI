export const fmtDate = (iso, opts = { day: 'numeric', month: 'short', year: 'numeric' }) =>
  iso ? new Date(iso).toLocaleDateString(undefined, opts) : '';

export const shortDate = (iso) => fmtDate(iso, { day: 'numeric', month: 'short' });
export const firstName = (name = '') => name.trim().split(/\s+/)[0] || 'there';
export const initials = (name = '') => name.trim().split(/\s+/).slice(0, 2).map((s) => s[0]?.toUpperCase()).join('') || '?';
export const plural = (n, one, many = `${one}s`) => `${n} ${n === 1 ? one : many}`;
