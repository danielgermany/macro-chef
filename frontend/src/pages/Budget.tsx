import { useState } from 'react';
import { useBudget } from '../hooks/useBudget';
import { useAuth } from '../contexts/AuthContext';
import { Skeleton, SkeletonCard } from '../components/ui/Skeleton';
import { DollarSign, TrendingUp, TrendingDown, AlertTriangle, Calendar, PieChart } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const COLORS = ['#22c55e', '#3b82f6', '#eab308', '#ef4444', '#a855f7', '#f97316', '#06b6d4'];

export function Budget() {
  const { user: authUser } = useAuth();
  const userId = authUser?.id || 1;
  const {
    weeklySummary,
    isLoadingWeekly,
    monthlySummary,
    isLoadingMonthly,
    spendingTrends,
    isLoadingTrends,
    categoryBreakdown,
    isLoadingCategories,
  } = useBudget(userId);

  const [viewMode, setViewMode] = useState<'weekly' | 'monthly'>('weekly');
  const summary = viewMode === 'weekly' ? weeklySummary : monthlySummary;
  const isLoading = viewMode === 'weekly' ? isLoadingWeekly : isLoadingMonthly;

  // Prepare data for charts
  const trendChartData =
    spendingTrends?.weekly_data?.map((week) => ({
      week: format(parseISO(week.week_start), 'MMM d'),
      spent: week.total_spent,
      budget: spendingTrends.weekly_budget || 0,
    })) || [];

  const categoryChartData =
    categoryBreakdown?.map((cat) => ({
      name: cat.category || 'Uncategorized',
      value: cat.total_spent,
      percentage: cat.percent_of_total,
    })) || [];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <Skeleton variant="text" width="30%" height={36} />
          <Skeleton variant="rectangular" width={200} height={40} />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Budget Tracker</h1>
          <p className="text-gray-500 mt-1">Monitor your grocery spending</p>
        </div>
        <div className="flex gap-2 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setViewMode('weekly')}
            className={`px-4 py-2 rounded-md transition-colors ${
              viewMode === 'weekly'
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Weekly
          </button>
          <button
            onClick={() => setViewMode('monthly')}
            className={`px-4 py-2 rounded-md transition-colors ${
              viewMode === 'monthly'
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Monthly
          </button>
        </div>
      </div>

      {/* Budget Summary Cards */}
      {summary && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Total Spent */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm text-gray-500">Total Spent</div>
                <DollarSign className="w-5 h-5 text-gray-400" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                ${summary.total_spent.toFixed(2)}
              </div>
              <div className="text-sm text-gray-500 mt-1">
                of ${summary.budget_limit.toFixed(2)}
              </div>
            </div>

            {/* Remaining */}
            <div
              className={`bg-white rounded-xl shadow-sm p-6 ${
                summary.is_over_budget ? 'border-2 border-red-500' : ''
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm text-gray-500">Remaining</div>
                {summary.is_over_budget ? (
                  <AlertTriangle className="w-5 h-5 text-red-500" />
                ) : summary.remaining > 0 ? (
                  <TrendingDown className="w-5 h-5 text-green-500" />
                ) : (
                  <TrendingUp className="w-5 h-5 text-yellow-500" />
                )}
              </div>
              <div
                className={`text-2xl font-bold ${
                  summary.is_over_budget
                    ? 'text-red-600'
                    : summary.remaining > 0
                    ? 'text-green-600'
                    : 'text-yellow-600'
                }`}
              >
                ${Math.abs(summary.remaining).toFixed(2)}
              </div>
              <div className="text-sm text-gray-500 mt-1">
                {summary.is_over_budget ? 'Over budget' : 'Under budget'}
              </div>
            </div>

            {/* Percentage Used */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm text-gray-500">Budget Used</div>
                <PieChart className="w-5 h-5 text-gray-400" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {summary.percentage_used.toFixed(1)}%
              </div>
              <div className="mt-2">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      summary.percentage_used > 100
                        ? 'bg-red-500'
                        : summary.percentage_used > 80
                        ? 'bg-yellow-500'
                        : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(summary.percentage_used, 100)}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Shopping Stats */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm text-gray-500">Shopping Trips</div>
                <Calendar className="w-5 h-5 text-gray-400" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {summary.num_trips || 0}
              </div>
              <div className="text-sm text-gray-500 mt-1">
                {summary.avg_per_trip
                  ? `Avg: $${summary.avg_per_trip.toFixed(2)}/trip`
                  : 'No trips yet'}
              </div>
            </div>
          </div>

          {/* Period Info */}
          <div className="bg-white rounded-xl shadow-sm p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-500">Period</div>
                <div className="font-semibold">
                  {format(parseISO(summary.period_start), 'MMM d')} -{' '}
                  {format(parseISO(summary.period_end), 'MMM d, yyyy')}
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-500">Daily Average</div>
                <div className="font-semibold">${summary.daily_average.toFixed(2)}</div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Spending Trends Chart */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">Spending Trends</h2>
          {isLoadingTrends ? (
            <div className="h-64 flex items-center justify-center text-gray-500">
              Loading trends...
            </div>
          ) : trendChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trendChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="week" />
                <YAxis />
                <Tooltip
                  formatter={(value: number) => `$${value.toFixed(2)}`}
                  labelStyle={{ color: '#374151' }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="spent"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  name="Spent"
                />
                <Line
                  type="monotone"
                  dataKey="budget"
                  stroke="#22c55e"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  name="Budget"
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              No spending data available
            </div>
          )}
          {spendingTrends && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Average Weekly Spending</span>
                <span className="font-semibold">
                  ${spendingTrends.avg_weekly_spending?.toFixed(2) || '0.00'}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm mt-2">
                <span className="text-gray-600">Trend</span>
                <span
                  className={`font-semibold ${
                    spendingTrends.is_trending_over ? 'text-red-600' : 'text-green-600'
                  }`}
                >
                  {spendingTrends.is_trending_over ? (
                    <>
                      <TrendingUp className="w-4 h-4 inline mr-1" />
                      Over by ${Math.abs(spendingTrends.avg_over_under || 0).toFixed(2)}/week
                    </>
                  ) : (
                    <>
                      <TrendingDown className="w-4 h-4 inline mr-1" />
                      Under by ${Math.abs(spendingTrends.avg_over_under || 0).toFixed(2)}/week
                    </>
                  )}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Category Breakdown */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">Category Breakdown</h2>
          {isLoadingCategories ? (
            <div className="h-64 flex items-center justify-center text-gray-500">
              Loading categories...
            </div>
          ) : categoryChartData.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsPieChart>
                  <Pie
                    data={categoryChartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percentage }) => `${name}: ${percentage}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {categoryChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
                </RechartsPieChart>
              </ResponsiveContainer>
              <div className="mt-4 space-y-2">
                {categoryBreakdown?.slice(0, 5).map((cat, index) => (
                  <div key={cat.category || 'uncategorized'} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: COLORS[index % COLORS.length] }}
                      />
                      <span className="text-sm font-medium">
                        {cat.category || 'Uncategorized'}
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-semibold">${cat.total_spent.toFixed(2)}</div>
                      <div className="text-xs text-gray-500">
                        {cat.percent_of_total.toFixed(1)}% • {cat.num_items} items
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              No category data available
            </div>
          )}
        </div>
      </div>

      {/* Category Breakdown Table */}
      {categoryBreakdown && categoryBreakdown.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">Detailed Category Breakdown</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Category</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Total Spent</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Items</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Avg Price</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">% of Total</th>
                </tr>
              </thead>
              <tbody>
                {categoryBreakdown.map((cat, index) => (
                  <tr key={cat.category || 'uncategorized'} className="border-b border-gray-100">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        />
                        <span className="font-medium">
                          {cat.category || 'Uncategorized'}
                        </span>
                      </div>
                    </td>
                    <td className="text-right py-3 px-4 font-semibold">
                      ${cat.total_spent.toFixed(2)}
                    </td>
                    <td className="text-right py-3 px-4 text-gray-600">{cat.num_items}</td>
                    <td className="text-right py-3 px-4 text-gray-600">
                      ${cat.avg_item_price.toFixed(2)}
                    </td>
                    <td className="text-right py-3 px-4">
                      <div className="flex items-center justify-end gap-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div
                            className="h-2 rounded-full"
                            style={{
                              width: `${cat.percent_of_total}%`,
                              backgroundColor: COLORS[index % COLORS.length],
                            }}
                          />
                        </div>
                        <span className="text-sm font-medium w-12 text-right">
                          {cat.percent_of_total.toFixed(1)}%
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!summary && !isLoading && (
        <div className="bg-white rounded-xl shadow-sm p-12 text-center">
          <DollarSign className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">No Budget Data</h2>
          <p className="text-gray-500">
            Start tracking your grocery spending by logging purchases in your meal plans.
          </p>
        </div>
      )}
    </div>
  );
}
