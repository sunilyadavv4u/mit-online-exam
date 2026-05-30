import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import toast from 'react-hot-toast';
import { authApi } from '../api/endpoints';
import { tokenStore } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    if (!tokenStore.getAccess()) {
      setUser(null);
      setLoading(false);
      return null;
    }
    try {
      const res = await authApi.me();
      setUser(res.data);
      return res.data;
    } catch (err) {
      tokenStore.clear();
      setUser(null);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = useCallback(async (email, password) => {
    const res = await authApi.login(email, password);
    tokenStore.set({ access: res.data.access, refresh: res.data.refresh });
    setUser(res.data.user);
    toast.success(`Welcome back, ${res.data.user.full_name || res.data.user.email}!`);
    return res.data.user;
  }, []);

  const register = useCallback(async (payload) => {
    const res = await authApi.register(payload);
    tokenStore.set({ access: res.data.access, refresh: res.data.refresh });
    setUser(res.data.user);
    toast.success('Account created! Please verify your email when convenient.');
    return res.data.user;
  }, []);

  const logout = useCallback(async () => {
    try {
      const refresh = tokenStore.getRefresh();
      if (refresh) await authApi.logout(refresh);
    } catch {
      /* ignore */
    } finally {
      tokenStore.clear();
      setUser(null);
      toast.success('Logged out');
    }
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, register, logout, refreshUser, setUser }),
    [user, loading, login, register, logout, refreshUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
