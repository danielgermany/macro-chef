import { useState } from 'react';
import { useDailyProgress, useLogMeal, useMealRecommendations } from '../hooks/useDailyProgress';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { RecipeSearch } from '../components/recipes/RecipeSearch';
import { Skeleton, SkeletonCard } from '../components/ui/Skeleton';
import { Plus, Search } from 'lucide-react';
import type { MealTime } from '../types/meal';
import type { Recipe } from '../services/recipeService';

export function MealTracker() {
  const { user: authUser } = useAuth();
  const userId = authUser?.id || 1;
  const { showSuccess, showError } = useToast();
  const { data: progress } = useDailyProgress(userId);
  const logMealMutation = useLogMeal(userId);
  
  const [showForm, setShowForm] = useState(false);
  const [showRecipeSearch, setShowRecipeSearch] = useState(false);
  const [mealTime, setMealTime] = useState<MealTime>('dinner');
  const [mealName, setMealName] = useState('');
  const [calories, setCalories] = useState('');
  const [protein, setProtein] = useState('');
  const [carbs, setCarbs] = useState('');
  const [fat, setFat] = useState('');

  const { data: recommendations } = useMealRecommendations(userId, mealTime, showForm);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    logMealMutation.mutate({
      meal_name: mealName,
      calories: parseInt(calories),
      protein_g: parseFloat(protein),
      carbs_g: parseFloat(carbs),
      fat_g: parseFloat(fat),
      meal_time: mealTime,
    }, {
      onSuccess: () => {
        setShowForm(false);
        setMealName('');
        setCalories('');
        setProtein('');
        setCarbs('');
        setFat('');
        showSuccess('Meal logged successfully!');
      },
      onError: () => {
        showError('Failed to log meal');
      },
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Meal Tracker</h1>
        <div className="flex gap-2">
          <button
            onClick={() => {
              setShowRecipeSearch(!showRecipeSearch);
              setShowForm(false);
            }}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Search className="w-5 h-5" />
            Search Recipes
          </button>
          <button
            onClick={() => {
              setShowForm(!showForm);
              setShowRecipeSearch(false);
            }}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Log Meal
          </button>
        </div>
      </div>

      {/* Recipe Search */}
      {showRecipeSearch && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">Search Online Recipes</h2>
          <RecipeSearch
            userId={userId}
            onSelectRecipe={(recipe) => {
              setMealName(recipe.title);
              setCalories(String(recipe.nutrition.calories));
              setProtein(String(recipe.nutrition.protein));
              setCarbs(String(recipe.nutrition.carbs));
              setFat(String(recipe.nutrition.fat));
              setShowRecipeSearch(false);
              setShowForm(true);
              showSuccess(`Added ${recipe.title} to meal form`);
            }}
            maxResults={12}
          />
        </div>
      )}

      {/* Log Meal Form */}
      {showForm && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">Log New Meal</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Meal Name
                </label>
                <input
                  type="text"
                  value={mealName}
                  onChange={(e) => setMealName(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Meal Time
                </label>
                <select
                  value={mealTime}
                  onChange={(e) => setMealTime(e.target.value as MealTime)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="breakfast">Breakfast</option>
                  <option value="lunch">Lunch</option>
                  <option value="dinner">Dinner</option>
                  <option value="snack">Snack</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Calories
                </label>
                <input
                  type="number"
                  value={calories}
                  onChange={(e) => setCalories(e.target.value)}
                  required
                  min="0"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Protein (g)
                </label>
                <input
                  type="number"
                  value={protein}
                  onChange={(e) => setProtein(e.target.value)}
                  required
                  min="0"
                  step="0.1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Carbs (g)
                </label>
                <input
                  type="number"
                  value={carbs}
                  onChange={(e) => setCarbs(e.target.value)}
                  required
                  min="0"
                  step="0.1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Fat (g)
                </label>
                <input
                  type="number"
                  value={fat}
                  onChange={(e) => setFat(e.target.value)}
                  required
                  min="0"
                  step="0.1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="flex gap-3">
              <button
                type="submit"
                disabled={logMealMutation.isPending}
                className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
              >
                {logMealMutation.isPending ? 'Logging...' : 'Log Meal'}
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>

          {/* Recommendations */}
          {recommendations && recommendations.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h3 className="text-lg font-semibold mb-3">Recommendations</h3>
              <div className="space-y-2">
                {recommendations.slice(0, 3).map((rec) => (
                  <button
                    key={rec.id || rec.name}
                    onClick={() => {
                      setMealName(rec.name);
                      setCalories(String(rec.calories));
                      setProtein(String(rec.protein_g));
                      setCarbs(String(rec.carbs_g));
                      setFat(String(rec.fat_g));
                    }}
                    className="w-full text-left p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="font-medium">{rec.name}</div>
                    <div className="text-sm text-gray-600">
                      {rec.calories} kcal | {rec.protein_g}g protein
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Today's Meals List */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">Today's Meals</h2>
        {progress?.meals && progress.meals.length > 0 ? (
          <div className="space-y-3">
            {progress.meals.map((meal) => (
              <div
                key={meal.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
              >
                <div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-gray-500 capitalize">
                      {meal.meal_time}
                    </span>
                    <span className="text-lg font-semibold">{meal.meal_name}</span>
                  </div>
                  <div className="flex gap-4 mt-2 text-sm text-gray-600">
                    <span>{meal.calories} kcal</span>
                    <span>{meal.protein_g}g protein</span>
                    <span>{meal.carbs_g}g carbs</span>
                    <span>{meal.fat_g}g fat</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No meals logged today</p>
        )}
      </div>
    </div>
  );
}
