import { useDailyProgress, useDeleteMeal } from '../hooks/useDailyProgress';
import { useUser } from '../hooks/useUser';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { MacroProgressCard } from '../components/dashboard/MacroProgressCard';
import { TodaysMeals } from '../components/dashboard/TodaysMeals';
import { QuickActions } from '../components/dashboard/QuickActions';
import { WeightChart } from '../components/dashboard/WeightChart';
import { Skeleton, SkeletonCard } from '../components/ui/Skeleton';

export function Dashboard() {
  const { user: authUser } = useAuth();
  const userId = authUser?.id || 1;
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/6ab49e72-b272-4456-a3cc-16544060033b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Dashboard.tsx:12',message:'Dashboard mounted',data:{authUserId:authUser?.id,resolvedUserId:userId,hasAuthUser:!!authUser},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
  // #endregion
  const { showSuccess, showError } = useToast();
  
  const { data: progress, isLoading: progressLoading } = useDailyProgress(userId);
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/6ab49e72-b272-4456-a3cc-16544060033b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Dashboard.tsx:17',message:'Daily progress query state',data:{hasProgress:!!progress,isLoading:progressLoading,hasTotals:!!progress?.totals,hasTargets:!!progress?.targets},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'F'})}).catch(()=>{});
  // #endregion
  const { data: user } = useUser(userId);
  const deleteMealMutation = useDeleteMeal(userId);

  const handleDeleteMeal = (mealId: number) => {
    if (window.confirm('Are you sure you want to delete this meal?')) {
      deleteMealMutation.mutate(mealId, {
        onSuccess: () => {
          showSuccess('Meal deleted successfully');
        },
        onError: () => {
          showError('Failed to delete meal');
        },
      });
    }
  };

  if (progressLoading) {
    return (
      <div className="space-y-6">
        <Skeleton variant="text" width="40%" height={36} />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <SkeletonCard />
          </div>
          <SkeletonCard />
        </div>
      </div>
    );
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
        <MacroProgressCard
          label="Calories"
          current={progress?.totals.calories || 0}
          target={progress?.targets.calories_target || 2000}
          unit="kcal"
          color="bg-green-500"
        />
        <MacroProgressCard
          label="Protein"
          current={progress?.totals.protein_g || 0}
          target={progress?.targets.protein_target_g || 150}
          unit="g"
          color="bg-red-500"
        />
        <MacroProgressCard
          label="Carbs"
          current={progress?.totals.carbs_g || 0}
          target={progress?.targets.carbs_target_g || 200}
          unit="g"
          color="bg-blue-500"
        />
        <MacroProgressCard
          label="Fat"
          current={progress?.totals.fat_g || 0}
          target={progress?.targets.fat_target_g || 70}
          unit="g"
          color="bg-yellow-500"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Today's Meals */}
        <div className="lg:col-span-2">
          <TodaysMeals meals={progress?.meals || []} onDelete={handleDeleteMeal} />
        </div>

        {/* Quick Actions */}
        <div>
          <QuickActions />
        </div>
      </div>

      {/* Weight Progress Chart */}
      <WeightChart userId={userId} days={30} />
    </div>
  );
}
