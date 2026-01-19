import { useState } from 'react';
import { useWeeklyPlanner } from '../hooks/useWeeklyPlanner';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { Skeleton, SkeletonCard } from '../components/ui/Skeleton';
import { Calendar, ShoppingCart, Save, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';
import { format, startOfWeek, addDays, addWeeks, subWeeks, isSameDay, parseISO } from 'date-fns';
import type { WeeklyPlan, DailyPlan, MealPlan } from '../services/planService';

const MEAL_TIMES: Array<'breakfast' | 'lunch' | 'dinner' | 'snack'> = [
  'breakfast',
  'lunch',
  'dinner',
  'snack',
];

const DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

export function WeeklyPlanner() {
  const { user: authUser } = useAuth();
  const userId = authUser?.id || 1;
  const { showSuccess, showError, showWarning } = useToast();
  const {
    generatePlan,
    generatePlanAsync,
    isGenerating,
    generatedPlan,
    savePlan,
    isSaving,
    savedPlans,
    isLoadingPlans,
    shoppingListQuery,
  } = useWeeklyPlanner(userId);

  const [currentWeekStart, setCurrentWeekStart] = useState(() => {
    const today = new Date();
    const monday = startOfWeek(today, { weekStartsOn: 1 });
    return monday;
  });

  const [showShoppingList, setShowShoppingList] = useState(false);
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null);
  const [planName, setPlanName] = useState('');

  const currentWeekEnd = addDays(currentWeekStart, 6);
  const weekDays = Array.from({ length: 7 }, (_, i) => addDays(currentWeekStart, i));

  const shoppingList = selectedPlanId ? shoppingListQuery(selectedPlanId).data : null;

  const handleGeneratePlan = async () => {
    const weekStartStr = format(currentWeekStart, 'yyyy-MM-dd');
    const name = planName.trim() || `Week of ${format(currentWeekStart, 'MMM d')}`;
    
    try {
      await generatePlanAsync({
        weekStart: weekStartStr,
        planName: name,
        autoRecommend: true,
      });
      showSuccess('Weekly plan generated successfully!');
    } catch (error) {
      console.error('Failed to generate plan:', error);
      showError('Failed to generate plan. Please try again.');
    }
  };

  const handleSavePlan = () => {
    if (!generatedPlan) {
      showError('No plan to save. Please generate a plan first.');
      return;
    }
    savePlan(generatedPlan, {
      onSuccess: () => {
        showSuccess('Plan saved successfully!');
      },
      onError: () => {
        showError('Failed to save plan');
      },
    });
  };

  const handleViewShoppingList = (planId: number) => {
    setSelectedPlanId(planId);
    setShowShoppingList(true);
  };

  const handlePreviousWeek = () => {
    setCurrentWeekStart(subWeeks(currentWeekStart, 1));
  };

  const handleNextWeek = () => {
    setCurrentWeekStart(addWeeks(currentWeekStart, 1));
  };

  const handleToday = () => {
    const today = new Date();
    const monday = startOfWeek(today, { weekStartsOn: 1 });
    setCurrentWeekStart(monday);
  };

  // Transform daily_plans to a map by date for easier lookup
  const planByDate = new Map<string, DailyPlan>();
  if (generatedPlan?.daily_plans) {
    // daily_plans is an array from generate_weekly_plan
    if (Array.isArray(generatedPlan.daily_plans)) {
      generatedPlan.daily_plans.forEach((dayPlan: any) => {
        // dayPlan.date is a date object or string
        const dateStr = typeof dayPlan.date === 'string' ? dayPlan.date : dayPlan.date;
        const dateKey = format(parseISO(dateStr), 'yyyy-MM-dd');
        
        // Transform meals from object (keyed by meal_time) to array
        const meals: MealPlan[] = Object.entries(dayPlan.meals || {}).map(([mealTime, mealData]: [string, any]) => ({
          meal_time: mealTime as 'breakfast' | 'lunch' | 'dinner' | 'snack',
          meal_name: mealData.meal_name || '',
          calories: mealData.calories || 0,
          protein_g: mealData.protein_g || 0,
          carbs_g: mealData.carbs_g || 0,
          fat_g: mealData.fat_g || 0,
          meal_template_id: mealData.meal_template_id,
          cost_estimate_usd: mealData.cost_estimate_usd,
        }));
        
        planByDate.set(dateKey, {
          date: dateKey,
          day_name: dayPlan.day_of_week || '',
          meals,
          daily_cost: dayPlan.daily_cost || 0,
          daily_nutrition: {
            calories: meals.reduce((sum, m) => sum + m.calories, 0),
            protein_g: meals.reduce((sum, m) => sum + m.protein_g, 0),
            carbs_g: meals.reduce((sum, m) => sum + m.carbs_g, 0),
            fat_g: meals.reduce((sum, m) => sum + m.fat_g, 0),
          },
        });
      });
    } else {
      // Handle object format (from get_plan) - keyed by day name
      Object.entries(generatedPlan.daily_plans).forEach(([dayName, meals]: [string, any]) => {
        const dayIndex = DAYS_OF_WEEK.findIndex((d) => d.toLowerCase() === dayName.toLowerCase());
        if (dayIndex >= 0) {
          const dayDate = addDays(currentWeekStart, dayIndex);
          const dateKey = format(dayDate, 'yyyy-MM-dd');
          const mealsArray: MealPlan[] = Array.isArray(meals) 
            ? meals 
            : [meals].map((m: any) => ({
                meal_time: m.meal_time,
                meal_name: m.meal_name || '',
                calories: m.calories || 0,
                protein_g: m.protein_g || 0,
                carbs_g: m.carbs_g || 0,
                fat_g: m.fat_g || 0,
                meal_template_id: m.meal_template_id,
                cost_estimate_usd: m.cost_estimate_usd,
              }));
          planByDate.set(dateKey, {
            date: dateKey,
            day_name: dayName,
            meals: mealsArray,
            daily_cost: mealsArray.reduce((sum, m) => sum + (m.cost_estimate_usd || 0), 0),
            daily_nutrition: {
              calories: mealsArray.reduce((sum, m) => sum + m.calories, 0),
              protein_g: mealsArray.reduce((sum, m) => sum + m.protein_g, 0),
              carbs_g: mealsArray.reduce((sum, m) => sum + m.carbs_g, 0),
              fat_g: mealsArray.reduce((sum, m) => sum + m.fat_g, 0),
            },
          });
        }
      });
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Weekly Planner</h1>
          <p className="text-gray-500 mt-1">
            Plan your meals for the week ahead
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleToday}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Today
          </button>
          <button
            onClick={handlePreviousWeek}
            className="p-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <button
            onClick={handleNextWeek}
            className="p-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Week Range Display */}
      <div className="bg-white rounded-xl shadow-sm p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">
              {format(currentWeekStart, 'MMM d')} - {format(currentWeekEnd, 'MMM d, yyyy')}
            </h2>
          </div>
          <div className="flex gap-3">
            <input
              type="text"
              placeholder="Plan name (optional)"
              value={planName}
              onChange={(e) => setPlanName(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <button
              onClick={handleGeneratePlan}
              disabled={isGenerating}
              className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
            >
              <RefreshCw className={`w-5 h-5 ${isGenerating ? 'animate-spin' : ''}`} />
              {isGenerating ? 'Generating...' : 'Generate Plan'}
            </button>
            {generatedPlan && (
              <button
                onClick={handleSavePlan}
                disabled={isSaving}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                <Save className="w-5 h-5" />
                {isSaving ? 'Saving...' : 'Save Plan'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Weekly Calendar */}
      {generatedPlan ? (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="grid grid-cols-7 border-b border-gray-200">
            {weekDays.map((day, index) => {
              const dateKey = format(day, 'yyyy-MM-dd');
              const dayPlan = planByDate.get(dateKey);
              const isToday = isSameDay(day, new Date());

              return (
                <div
                  key={dateKey}
                  className={`border-r border-gray-200 last:border-r-0 ${
                    isToday ? 'bg-primary-50' : ''
                  }`}
                >
                  <div className={`p-3 text-center ${isToday ? 'bg-primary-600 text-white' : 'bg-gray-50'}`}>
                    <div className="text-sm font-medium">{DAYS_OF_WEEK[index]}</div>
                    <div className={`text-lg font-bold ${isToday ? 'text-white' : 'text-gray-900'}`}>
                      {format(day, 'd')}
                    </div>
                  </div>
                  <div className="p-3 space-y-2 min-h-[400px]">
                    {MEAL_TIMES.map((mealTime) => {
                      const meal = dayPlan?.meals.find((m) => m.meal_time === mealTime);
                      return (
                        <div
                          key={mealTime}
                          className="border border-gray-200 rounded-lg p-2 hover:border-primary-300 transition-colors"
                        >
                          <div className="text-xs font-medium text-gray-500 uppercase mb-1">
                            {mealTime}
                          </div>
                          {meal ? (
                            <div>
                              <div className="font-semibold text-sm">{meal.meal_name}</div>
                              <div className="text-xs text-gray-600 mt-1">
                                {meal.calories} kcal | P: {meal.protein_g.toFixed(0)}g | C:{' '}
                                {meal.carbs_g.toFixed(0)}g | F: {meal.fat_g.toFixed(0)}g
                              </div>
                              {meal.cost_estimate_usd && (
                                <div className="text-xs text-gray-500 mt-1">
                                  ${meal.cost_estimate_usd.toFixed(2)}
                                </div>
                              )}
                            </div>
                          ) : (
                            <div className="text-xs text-gray-400 italic">No meal planned</div>
                          )}
                        </div>
                      );
                    })}
                    {dayPlan && (
                      <div className="mt-2 pt-2 border-t border-gray-200">
                        <div className="text-xs text-gray-600">
                          <div>Total: {dayPlan.daily_nutrition.calories.toFixed(0)} kcal</div>
                          <div>Cost: ${dayPlan.daily_cost.toFixed(2)}</div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm p-12 text-center">
          <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">No Plan Generated</h2>
          <p className="text-gray-500 mb-6">
            Generate a weekly meal plan based on your preferences and goals.
          </p>
          <button
            onClick={handleGeneratePlan}
            disabled={isGenerating}
            className="flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors mx-auto"
          >
            <RefreshCw className={`w-5 h-5 ${isGenerating ? 'animate-spin' : ''}`} />
            {isGenerating ? 'Generating...' : 'Generate Weekly Plan'}
          </button>
        </div>
      )}

      {/* Plan Summary */}
      {generatedPlan && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="text-sm text-gray-500 mb-1">Total Weekly Cost</div>
            <div className="text-2xl font-bold text-green-600">
              ${generatedPlan.total_cost_estimate.toFixed(2)}
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="text-sm text-gray-500 mb-1">Plan Name</div>
            <div className="text-lg font-semibold">{generatedPlan.plan_name || 'Untitled Plan'}</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <button
              onClick={() => {
                if (savedPlans.length > 0) {
                  handleViewShoppingList(savedPlans[0].id);
                }
              }}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors w-full justify-center"
            >
              <ShoppingCart className="w-5 h-5" />
              Generate Shopping List
            </button>
          </div>
        </div>
      )}

      {/* Saved Plans */}
      {savedPlans.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">Saved Plans</h2>
          <div className="space-y-2">
            {savedPlans.map((plan) => (
              <div
                key={plan.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div>
                  <div className="font-semibold">{plan.plan_name}</div>
                  <div className="text-sm text-gray-500">
                    {format(parseISO(plan.week_start_date), 'MMM d')} -{' '}
                    {format(parseISO(plan.week_end_date), 'MMM d, yyyy')}
                  </div>
                </div>
                <div className="flex gap-2">
                  <div className="text-right">
                    <div className="font-semibold">${plan.total_cost_estimate_usd.toFixed(2)}</div>
                    <div className="text-xs text-gray-500">Total cost</div>
                  </div>
                  <button
                    onClick={() => handleViewShoppingList(plan.id)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="View Shopping List"
                  >
                    <ShoppingCart className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Shopping List Modal */}
      {showShoppingList && shoppingList && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-lg max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-2xl font-bold">Shopping List</h2>
              <button
                onClick={() => {
                  setShowShoppingList(false);
                  setSelectedPlanId(null);
                }}
                className="text-gray-500 hover:text-gray-700"
              >
                ×
              </button>
            </div>
            <div className="p-6">
              <div className="mb-6">
                <div className="text-sm text-gray-500 mb-1">Total Estimated Cost</div>
                <div className="text-3xl font-bold text-green-600">
                  ${shoppingList.total_estimated_cost.toFixed(2)}
                </div>
              </div>

              {Object.entries(shoppingList.grouped_by_category).map(([category, items]) => (
                <div key={category} className="mb-6">
                  <h3 className="text-lg font-semibold mb-3 capitalize">{category}</h3>
                  <div className="space-y-2">
                    {items.map((item, index) => (
                      <div
                        key={index}
                        className="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
                      >
                        <div>
                          <div className="font-medium">{item.item_name}</div>
                          <div className="text-sm text-gray-500">
                            {item.quantity} {item.unit}
                          </div>
                        </div>
                        {item.estimated_cost && (
                          <div className="font-semibold">${item.estimated_cost.toFixed(2)}</div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
