import { useState } from 'react';
import { useDailyProgress, useLogMeal, useMealRecommendations } from '../hooks/useDailyProgress';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { RecipeSearch } from '../components/recipes/RecipeSearch';
import { MealHistory } from '../components/meals/MealHistory';
import { FormField } from '../components/forms/FormField';
import { Skeleton, SkeletonCard } from '../components/ui/Skeleton';
import { Plus, Search, History } from 'lucide-react';
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
  const [showHistory, setShowHistory] = useState(false);
  const [mealTime, setMealTime] = useState<MealTime>('dinner');
  const [mealName, setMealName] = useState('');
  const [calories, setCalories] = useState('');
  const [protein, setProtein] = useState('');
  const [carbs, setCarbs] = useState('');
  const [fat, setFat] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const { data: recommendations } = useMealRecommendations(userId, mealTime, showForm);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!mealName.trim()) {
      newErrors.mealName = 'Meal name is required';
    }

    const caloriesNum = parseInt(calories);
    if (!calories || isNaN(caloriesNum) || caloriesNum < 0) {
      newErrors.calories = 'Valid calories amount is required';
    }

    const proteinNum = parseFloat(protein);
    if (protein === '' || isNaN(proteinNum) || proteinNum < 0) {
      newErrors.protein = 'Valid protein amount is required';
    }

    const carbsNum = parseFloat(carbs);
    if (carbs === '' || isNaN(carbsNum) || carbsNum < 0) {
      newErrors.carbs = 'Valid carbs amount is required';
    }

    const fatNum = parseFloat(fat);
    if (fat === '' || isNaN(fatNum) || fatNum < 0) {
      newErrors.fat = 'Valid fat amount is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

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
        setErrors({});
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
              setShowHistory(!showHistory);
              setShowForm(false);
              setShowRecipeSearch(false);
            }}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              showHistory
                ? 'bg-gray-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <History className="w-5 h-5" />
            History
          </button>
          <button
            onClick={() => {
              setShowRecipeSearch(!showRecipeSearch);
              setShowForm(false);
              setShowHistory(false);
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
              setShowHistory(false);
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
              <FormField label="Meal Name" error={errors.mealName} required>
                <input
                  type="text"
                  value={mealName}
                  onChange={(e) => {
                    setMealName(e.target.value);
                    if (errors.mealName) setErrors({ ...errors, mealName: '' });
                  }}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    errors.mealName ? 'border-red-300' : 'border-gray-300'
                  }`}
                />
              </FormField>
              <FormField label="Meal Time">
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
              </FormField>
            </div>

            <div className="grid grid-cols-4 gap-4">
              <FormField label="Calories" error={errors.calories} required>
                <input
                  type="number"
                  value={calories}
                  onChange={(e) => {
                    setCalories(e.target.value);
                    if (errors.calories) setErrors({ ...errors, calories: '' });
                  }}
                  min="0"
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    errors.calories ? 'border-red-300' : 'border-gray-300'
                  }`}
                />
              </FormField>
              <FormField label="Protein (g)" error={errors.protein} required>
                <input
                  type="number"
                  value={protein}
                  onChange={(e) => {
                    setProtein(e.target.value);
                    if (errors.protein) setErrors({ ...errors, protein: '' });
                  }}
                  min="0"
                  step="0.1"
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    errors.protein ? 'border-red-300' : 'border-gray-300'
                  }`}
                />
              </FormField>
              <FormField label="Carbs (g)" error={errors.carbs} required>
                <input
                  type="number"
                  value={carbs}
                  onChange={(e) => {
                    setCarbs(e.target.value);
                    if (errors.carbs) setErrors({ ...errors, carbs: '' });
                  }}
                  min="0"
                  step="0.1"
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    errors.carbs ? 'border-red-300' : 'border-gray-300'
                  }`}
                />
              </FormField>
              <FormField label="Fat (g)" error={errors.fat} required>
                <input
                  type="number"
                  value={fat}
                  onChange={(e) => {
                    setFat(e.target.value);
                    if (errors.fat) setErrors({ ...errors, fat: '' });
                  }}
                  min="0"
                  step="0.1"
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    errors.fat ? 'border-red-300' : 'border-gray-300'
                  }`}
                />
              </FormField>
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

      {/* Meal History */}
      {showHistory && <MealHistory userId={userId} />}

      {/* Today's Meals List */}
      {!showHistory && (
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
      )}
    </div>
  );
}
