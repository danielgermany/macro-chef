import type { MealLog } from '../../types/meal';
import { Clock, Trash2 } from 'lucide-react';

interface TodaysMealsProps {
  meals: MealLog[];
  onDelete?: (mealId: number) => void;
}

export function TodaysMeals({ meals, onDelete }: TodaysMealsProps) {
  if (meals.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">Today's Meals</h2>
        <p className="text-gray-500 text-center py-8">No meals logged today</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <h2 className="text-xl font-semibold mb-4">Today's Meals</h2>
      <div className="space-y-3">
        {meals.map((meal) => (
          <div
            key={meal.id}
            className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="flex-1">
              <div className="flex items-center gap-3">
                <Clock className="w-4 h-4 text-gray-400" />
                <span className="text-sm font-medium text-gray-500 capitalize">
                  {meal.meal_time}
                </span>
              </div>
              <h3 className="text-lg font-semibold mt-1">{meal.meal_name}</h3>
              <div className="flex gap-4 mt-2 text-sm text-gray-600">
                <span>{meal.calories} kcal</span>
                <span>{meal.protein_g}g protein</span>
                <span>{meal.carbs_g}g carbs</span>
                <span>{meal.fat_g}g fat</span>
              </div>
            </div>
            {onDelete && (
              <button
                onClick={() => onDelete(meal.id)}
                className="ml-4 p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                title="Delete meal"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
