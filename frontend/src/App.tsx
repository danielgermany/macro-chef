import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { Layout } from './components/layout/Layout';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { MealTracker } from './pages/MealTracker';
import { Recipes } from './pages/Recipes';
import { Nutrition } from './pages/Nutrition';
import { Inventory } from './pages/Inventory';
import { WeeklyPlanner } from './pages/WeeklyPlanner';
import { Budget } from './pages/Budget';
import { Settings } from './pages/Settings';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              {/* Protected routes */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <Layout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="meals" element={<MealTracker />} />
                <Route path="recipes" element={<Recipes />} />
                <Route path="nutrition" element={<Nutrition />} />
                <Route path="inventory" element={<Inventory />} />
                <Route path="planner" element={<WeeklyPlanner />} />
                <Route path="budget" element={<Budget />} />
                <Route path="settings" element={<Settings />} />
              </Route>
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </ToastProvider>
    </QueryClientProvider>
  );
}

export default App;
