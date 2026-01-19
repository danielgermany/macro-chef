import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { api } from '../services/api';
import type { User } from '../types/user';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (data: RegisterData) => Promise<void>;
}

interface RegisterData {
  email: string;
  password: string;
  name: string;
  age?: number;
  sex?: string;
  height_inches?: number;
  weight_lbs?: number;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for stored token on mount
    const token = localStorage.getItem('token');
    if (token) {
      // Set token in API client
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // Fetch current user
      api.get('/auth/me')
        .then((res) => {
          setUser(res.data);
        })
        .catch(() => {
          // Token invalid, remove it
          localStorage.removeItem('token');
          delete api.defaults.headers.common['Authorization'];
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/6ab49e72-b272-4456-a3cc-16544060033b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.tsx:56',message:'Login attempt started',data:{email},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    const response = await api.post('/auth/login-json', { email, password });
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/6ab49e72-b272-4456-a3cc-16544060033b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.tsx:58',message:'Login API response received',data:{hasToken:!!response.data.access_token,tokenLength:response.data.access_token?.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    const { access_token } = response.data;
    
    // Store token
    localStorage.setItem('token', access_token);
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/6ab49e72-b272-4456-a3cc-16544060033b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.tsx:63',message:'Token stored in localStorage',data:{storedToken:localStorage.getItem('token')?.substring(0,20)+'...'},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/6ab49e72-b272-4456-a3cc-16544060033b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.tsx:64',message:'Token set in API headers',data:{hasAuthHeader:!!api.defaults.headers.common['Authorization']},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
    // #endregion
    
    // Fetch user data
    const userResponse = await api.get('/auth/me');
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/6ab49e72-b272-4456-a3cc-16544060033b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.tsx:67',message:'User data fetched',data:{userId:userResponse.data?.id,userName:userResponse.data?.name},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
    // #endregion
    setUser(userResponse.data);
  };

  const logout = () => {
    localStorage.removeItem('token');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
  };

  const register = async (data: RegisterData) => {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/6ab49e72-b272-4456-a3cc-16544060033b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.tsx:75',message:'Registration attempt started',data:{email:data.email,hasName:!!data.name},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    const response = await api.post('/auth/register', data);
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/6ab49e72-b272-4456-a3cc-16544060033b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.tsx:77',message:'Registration API response received',data:{userId:response.data?.id,status:response.status},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    
    // After registration, automatically log in
    await login(data.email, data.password);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        logout,
        register,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
