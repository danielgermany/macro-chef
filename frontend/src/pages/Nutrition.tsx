import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { nutritionService } from '../services/nutritionService';
import { useUser } from '../hooks/useUser';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { Skeleton, SkeletonCard } from '../components/ui/Skeleton';
import { Target, TrendingUp } from 'lucide-react';

export function Nutrition() {
  const { user: authUser } = useAuth();
  const userId = authUser?.id || 1;
  const { data: user } = useUser(userId);
  const { showSuccess, showError } = useToast();
  const queryClient = useQueryClient();
  
  const { data: targets, isLoading } = useQuery({
    queryKey: ['nutritionTargets', userId],
    queryFn: () => nutritionService.getTodayTargets(userId),
  });

  const generateTargetsMutation = useMutation({
    mutationFn: () => nutritionService.generateTargets(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nutritionTargets', userId] });
      showSuccess('Nutrition targets generated successfully');
    },
    onError: () => {
      showError('Failed to generate targets');
    },
  });

  const handleGenerateTargets = () => {
    if (window.confirm('Generate new targets for today? This will overwrite existing targets.')) {
      generateTargetsMutation.mutate();
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <Skeleton variant="text" width="30%" height={36} />
          <Skeleton variant="rectangular" width={180} height={40} />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Nutrition Targets</h1>
        <button
          onClick={handleGenerateTargets}
          disabled={generateTargetsMutation.isPending}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
        >
          <Target className="w-5 h-5" />
          {generateTargetsMutation.isPending ? 'Generating...' : 'Generate Targets'}
        </button>
      </div>

      {targets ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Daily Targets */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Target className="w-5 h-5 text-primary-600" />
              Today's Targets
            </h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-700">Calories</span>
                <span className="text-xl font-bold">{targets.calories_target?.toLocaleString() || 0} kcal</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                <span className="text-gray-700">Protein</span>
                <span className="text-xl font-bold text-red-600">{targets.protein_target_g || 0}g</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                <span className="text-gray-700">Carbs</span>
                <span className="text-xl font-bold text-blue-600">{targets.carbs_target_g || 0}g</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                <span className="text-gray-700">Fat</span>
                <span className="text-xl font-bold text-yellow-600">{targets.fat_target_g || 0}g</span>
              </div>
              {targets.fiber_target_g && (
                <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                  <span className="text-gray-700">Fiber</span>
                  <span className="text-xl font-bold text-green-600">{targets.fiber_target_g}g</span>
                </div>
              )}
            </div>
          </div>

          {/* User Info */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-primary-600" />
              Your Profile
            </h2>
            {user && (
              <div className="space-y-3">
                <div>
                  <span className="text-sm text-gray-500">Goal</span>
                  <p className="font-semibold capitalize">{user.goal_type}</p>
                </div>
                <div>
                  <span className="text-sm text-gray-500">Activity Level</span>
                  <p className="font-semibold capitalize">{user.activity_level}</p>
                </div>
                <div>
                  <span className="text-sm text-gray-500">Current Weight</span>
                  <p className="font-semibold">{user.weight_lbs} lbs</p>
                </div>
                <div>
                  <span className="text-sm text-gray-500">Weekly Budget</span>
                  <p className="font-semibold">${user.weekly_budget_usd}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm p-6 text-center py-12">
          <Target className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">No Targets Generated</h2>
          <p className="text-gray-500 mb-4">
            Generate daily nutrition targets based on your profile and goals.
          </p>
          <button
            onClick={handleGenerateTargets}
            disabled={generateTargetsMutation.isPending}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            {generateTargetsMutation.isPending ? 'Generating...' : 'Generate Targets'}
          </button>
        </div>
      )}
    </div>
  );
}
