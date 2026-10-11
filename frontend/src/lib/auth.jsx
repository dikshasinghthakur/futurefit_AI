import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { api, tokenStore } from './api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const qc = useQueryClient();
  const [user, setUser] = useState(null);
  const [booting, setBooting] = useState(() => !!tokenStore.access);

  useEffect(() => {
    if (!tokenStore.access) return;
    api.get('/auth/me').then(setUser).catch(() => tokenStore.clear()).finally(() => setBooting(false));
  }, []);

  useEffect(() => {
    const onLogout = () => { setUser(null); qc.clear(); };
    window.addEventListener('auth:logout', onLogout);
    return () => window.removeEventListener('auth:logout', onLogout);
  }, [qc]);

  const finish = useCallback((data) => { tokenStore.set(data); setUser(data.user); }, []);
  const login = useCallback(async (email, password) => finish(await api.authPost('/auth/login', { email, password })), [finish]);
  const register = useCallback(async (name, email, password) => finish(await api.authPost('/auth/register', { name, email, password })), [finish]);
  const logout = useCallback(() => { tokenStore.clear(); setUser(null); qc.clear(); }, [qc]);

  const value = useMemo(() => ({ user, setUser, booting, login, register, logout }), [user, booting, login, register, logout]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
