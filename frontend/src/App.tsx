import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { MealTracker } from './pages/MealTracker';
import { Nutrition } from './pages/Nutrition';
import { Inventory } from './pages/Inventory';
import { WeeklyPlanner } from './pages/WeeklyPlanner';
import { Budget } from './pages/Budget';
import { Settings } from './pages/Settings';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="meals" element={<MealTracker />} />
            <Route path="nutrition" element={<Nutrition />} />
            <Route path="inventory" element={<Inventory />} />
            <Route path="planner" element={<WeeklyPlanner />} />
            <Route path="budget" element={<Budget />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
