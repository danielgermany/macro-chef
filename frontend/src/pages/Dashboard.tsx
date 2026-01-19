import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';

export function Dashboard() {
  const userId = 1; // TODO: Get from auth context
  
  const { data: progress, isLoading: progressLoading } = useQuery({
    queryKey: ['dailyProgress', userId],
    queryFn: () => api.get(`/meals/progress?user_id=${userId}`).then(r => r.data),
  });

  const { data: user } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => api.get(`/users/${userId}`).then(r => r.data),
  });

  if (progressLoading) {
    return <div className="animate-pulse">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.name || 'Chef'}! 👋
        </h1>
        <p className="text-gray-500 mt-1">
          Here's your nutrition summary for today
        </p>
      </div>

      {/* Macro Progress Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <p className="text-sm text-gray-500">Calories</p>
          <p className="text-2xl font-bold">
            {progress?.totals.calories || 0}
            <span className="text-sm font-normal text-gray-400 ml-1">
              / {progress?.targets.calories_target || 2000} kcal
            </span>
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6">
          <p className="text-sm text-gray-500">Protein</p>
          <p className="text-2xl font-bold">
            {progress?.totals.protein_g || 0}
            <span className="text-sm font-normal text-gray-400 ml-1">
              / {progress?.targets.protein_target_g || 150}g
            </span>
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6">
          <p className="text-sm text-gray-500">Carbs</p>
          <p className="text-2xl font-bold">
            {progress?.totals.carbs_g || 0}
            <span className="text-sm font-normal text-gray-400 ml-1">
              / {progress?.targets.carbs_target_g || 200}g
            </span>
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6">
          <p className="text-sm text-gray-500">Fat</p>
          <p className="text-2xl font-bold">
            {progress?.totals.fat_g || 0}
            <span className="text-sm font-normal text-gray-400 ml-1">
              / {progress?.targets.fat_target_g || 70}g
            </span>
          </p>
        </div>
      </div>

      {/* Placeholder for more content */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">Today's Meals</h2>
        <p className="text-gray-500">Meal list will be displayed here</p>
      </div>
    </div>
  );
}
