import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
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
    const response = await api.post('/auth/login-json', { email, password });
    const { access_token } = response.data;
    
    // Store token
    localStorage.setItem('token', access_token);
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    
    // Fetch user data
    const userResponse = await api.get('/auth/me');
    setUser(userResponse.data);
  };

  const logout = () => {
    localStorage.removeItem('token');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
  };

  const register = async (data: RegisterData) => {
    const response = await api.post('/auth/register', data);
    
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
