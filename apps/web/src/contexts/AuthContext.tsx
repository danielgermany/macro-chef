import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { apiLogin, apiMe, apiRegister } from '../lib/api';

const STORAGE_KEY = 'access_token';

interface AuthState {
  token: string | null;
  email: string | null;
  isReady: boolean;
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, displayName?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(STORAGE_KEY));
  const [email, setEmail] = useState<string | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const t = localStorage.getItem(STORAGE_KEY);
    if (!t) {
      setIsReady(true);
      return;
    }
    apiMe()
      .then((data) => {
        setEmail(data.user.email);
      })
      .catch(() => {
        localStorage.removeItem(STORAGE_KEY);
        setToken(null);
      })
      .finally(() => setIsReady(true));
  }, []);

  const login = useCallback(async (e: string, password: string) => {
    const { accessToken } = await apiLogin({ email: e, password });
    localStorage.setItem(STORAGE_KEY, accessToken);
    setToken(accessToken);
    const me = await apiMe();
    setEmail(me.user.email);
  }, []);

  const register = useCallback(async (e: string, password: string, displayName?: string) => {
    const { accessToken } = await apiRegister({ email: e, password, displayName });
    localStorage.setItem(STORAGE_KEY, accessToken);
    setToken(accessToken);
    const me = await apiMe();
    setEmail(me.user.email);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setToken(null);
    setEmail(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      email,
      isReady,
      login,
      register,
      logout,
    }),
    [token, email, isReady, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return ctx;
}
