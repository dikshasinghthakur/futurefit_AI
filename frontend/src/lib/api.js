const API_HOST = import.meta.env.VITE_API_HOST;
const BASE = import.meta.env.VITE_API_URL || (API_HOST ? `https://${API_HOST}/api` : '/api');
const ACCESS = 'ff_access';
const REFRESH = 'ff_refresh';

export const tokenStore = {
  get access() { return localStorage.getItem(ACCESS); },
  get refresh() { return localStorage.getItem(REFRESH); },
  set({ access_token, refresh_token }) {
    localStorage.setItem(ACCESS, access_token);
    if (refresh_token) localStorage.setItem(REFRESH, refresh_token);
  },
  clear() { localStorage.removeItem(ACCESS); localStorage.removeItem(REFRESH); },
};

export class ApiError extends Error {
  constructor(status, message) { super(message); this.status = status; }
}

let refreshing = null;
function refreshTokens() {
  if (!tokenStore.refresh) return Promise.resolve(false);
  if (!refreshing) {
    refreshing = fetch(`${BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: tokenStore.refresh }),
    })
      .then(async (r) => {
        if (!r.ok) throw new Error('refresh failed');
        tokenStore.set(await r.json());
        return true;
      })
      .catch(() => {
        tokenStore.clear();
        window.dispatchEvent(new Event('auth:logout'));
        return false;
      })
      .finally(() => { refreshing = null; }); // concurrent 401s share one refresh call
  }
  return refreshing;
}

function messageFrom(detail, fallback) {
  if (!detail) return fallback;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map((d) => d.msg?.replace(/^Value error, /, '') || '').filter(Boolean).join('. ') || fallback;
  return fallback;
}

async function request(path, { method = 'GET', json, form, auth = true, retried = false } = {}) {
  const headers = {};
  if (auth && tokenStore.access) headers.Authorization = `Bearer ${tokenStore.access}`;
  let body;
  if (json !== undefined) { headers['Content-Type'] = 'application/json'; body = JSON.stringify(json); }
  else if (form) body = form;

  let res;
  try {
    res = await fetch(`${BASE}${path}`, { method, headers, body });
  } catch {
    throw new ApiError(0, "Can't reach the server. Check your connection and try again.");
  }

  if (res.status === 401 && auth && !retried && (await refreshTokens())) {
    return request(path, { method, json, form, auth, retried: true });
  }
  if (!res.ok) {
    let detail;
    try { detail = (await res.json()).detail; } catch { /* non-JSON error */ }
    throw new ApiError(res.status, messageFrom(detail, `Something went wrong (${res.status}).`));
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  get: (p) => request(p),
  post: (p, json) => request(p, { method: 'POST', json }),
  put: (p, json) => request(p, { method: 'PUT', json }),
  patch: (p, json) => request(p, { method: 'PATCH', json }),
  del: (p) => request(p, { method: 'DELETE' }),
  upload: (p, form) => request(p, { method: 'POST', form }),
  authPost: (p, json) => request(p, { method: 'POST', json, auth: false }),
};
