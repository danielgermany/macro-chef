import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { mealService } from '../../services/mealService';
import { Search, Filter, X } from 'lucide-react';
import { format } from 'date-fns';
import type { MealLog } from '../../types/meal';

interface MealHistoryProps {
  userId: number;
}

export function MealHistory({ userId }: MealHistoryProps) {
  const [showFilters, setShowFilters] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [daysFilter, setDaysFilter] = useState<number | null>(7);
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [useDateRange, setUseDateRange] = useState(false);

  const { data: meals, isLoading } = useQuery({
    queryKey: ['mealHistory', userId, daysFilter, startDate, endDate, searchQuery],
    queryFn: () =>
      mealService.getMealHistory(userId, {
        days: useDateRange ? undefined : daysFilter || undefined,
        startDate: useDateRange && startDate ? startDate : undefined,
        endDate: useDateRange && endDate ? endDate : undefined,
        mealName: searchQuery || undefined,
      }),
  });

  const handleClearFilters = () => {
    setSearchQuery('');
    setDaysFilter(7);
    setStartDate('');
    setEndDate('');
    setUseDateRange(false);
  };

  const hasActiveFilters = searchQuery || useDateRange || daysFilter !== 7;

  // Group meals by date
  const mealsByDate = meals?.reduce((acc: Record<string, MealLog[]>, meal) => {
    const date = meal.date;
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(meal);
    return acc;
  }, {}) || {};

  const sortedDates = Object.keys(mealsByDate).sort((a, b) => 
    new Date(b).getTime() - new Date(a).getTime()
  );

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Meal History</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
              showFilters || hasActiveFilters
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <Filter className="w-4 h-4" />
            Filters
          </button>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-medium">Filter Options</h3>
            {hasActiveFilters && (
              <button
                onClick={handleClearFilters}
                className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
              >
                <X className="w-4 h-4" />
                Clear All
              </button>
            )}
          </div>

          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search by Meal Name
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-4 w-4 text-gray-400" />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search meals..."
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Date Range Toggle */}
          <div>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={useDateRange}
                onChange={(e) => {
                  setUseDateRange(e.target.checked);
                  if (!e.target.checked) {
                    setStartDate('');
                    setEndDate('');
                  }
                }}
                className="rounded"
              />
              <span className="text-sm font-medium text-gray-700">Use Date Range</span>
            </label>
          </div>

          {/* Date Range or Days Filter */}
          {useDateRange ? (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Start Date
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  max={endDate || format(new Date(), 'yyyy-MM-dd')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  End Date
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  min={startDate}
                  max={format(new Date(), 'yyyy-MM-dd')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Last N Days
              </label>
              <select
                value={daysFilter || ''}
                onChange={(e) => setDaysFilter(e.target.value ? parseInt(e.target.value) : null)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="7">Last 7 days</option>
                <option value="14">Last 14 days</option>
                <option value="30">Last 30 days</option>
                <option value="60">Last 60 days</option>
                <option value="90">Last 90 days</option>
              </select>
            </div>
          )}
        </div>
      )}

      {/* Results */}
      {isLoading ? (
        <div className="text-center py-8 text-gray-500">Loading meal history...</div>
      ) : sortedDates.length > 0 ? (
        <div className="space-y-6">
          {sortedDates.map((date) => (
            <div key={date}>
              <h3 className="text-lg font-semibold mb-3 text-gray-800">
                {format(new Date(date), 'EEEE, MMMM d, yyyy')}
              </h3>
              <div className="space-y-2">
                {mealsByDate[date].map((meal) => (
                  <div
                    key={meal.id}
                    className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-medium text-gray-500 capitalize px-2 py-1 bg-gray-100 rounded">
                          {meal.meal_time}
                        </span>
                        <span className="font-semibold">{meal.meal_name}</span>
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
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          {hasActiveFilters ? 'No meals found matching your filters.' : 'No meal history available.'}
        </div>
      )}
    </div>
  );
}
