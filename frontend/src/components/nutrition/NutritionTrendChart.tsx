import { useQuery } from '@tanstack/react-query';
import { mealService } from '../../services/mealService';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format, subDays } from 'date-fns';
import { Skeleton } from '../ui/Skeleton';

interface NutritionTrendChartProps {
  userId: number;
  days?: number;
}

export function NutritionTrendChart({ userId, days = 7 }: NutritionTrendChartProps) {
  const { data: progressData, isLoading } = useQuery({
    queryKey: ['nutritionTrend', userId, days],
    queryFn: async () => {
      const data = [];
      const today = new Date();
      for (let i = days - 1; i >= 0; i--) {
        const date = subDays(today, i);
        const dateStr = format(date, 'yyyy-MM-dd');
        try {
          const progress = await mealService.getDailyProgress(userId, dateStr);
          data.push({
            date: dateStr,
            dateLabel: format(date, 'MMM d'),
            calories: progress.totals?.calories || 0,
            protein: progress.totals?.protein_g || 0,
            carbs: progress.totals?.carbs_g || 0,
            fat: progress.totals?.fat_g || 0,
            caloriesTarget: progress.targets?.calories_target || 0,
            proteinTarget: progress.targets?.protein_target_g || 0,
            carbsTarget: progress.targets?.carbs_target_g || 0,
            fatTarget: progress.targets?.fat_target_g || 0,
          });
        } catch {
          // Skip days with no data
          data.push({
            date: dateStr,
            dateLabel: format(date, 'MMM d'),
            calories: 0,
            protein: 0,
            carbs: 0,
            fat: 0,
            caloriesTarget: 0,
            proteinTarget: 0,
            carbsTarget: 0,
            fatTarget: 0,
          });
        }
      }
      return data;
    },
  });

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6">
        <Skeleton variant="text" width="40%" height={28} className="mb-4" />
        <Skeleton variant="rectangular" width="100%" height={300} />
      </div>
    );
  }

  if (!progressData || progressData.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Nutrition Trends</h3>
        <div className="h-64 flex items-center justify-center text-gray-500">
          No nutrition data available
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <h3 className="text-lg font-semibold mb-4">Nutrition Trends (Last {days} Days)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={progressData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="dateLabel" />
          <YAxis yAxisId="left" label={{ value: 'Calories', angle: -90, position: 'insideLeft' }} />
          <YAxis
            yAxisId="right"
            orientation="right"
            label={{ value: 'Macros (g)', angle: 90, position: 'insideRight' }}
          />
          <Tooltip
            formatter={(value: number | undefined, name: string | undefined) => {
              const nameStr = name || 'Unknown';
              if (value === undefined) return ['N/A', nameStr] as [string, string];
              if (nameStr.includes('Target')) return [`${value.toFixed(0)}`, nameStr] as [string, string];
              if (nameStr === 'calories' || nameStr === 'caloriesTarget') return [`${value.toFixed(0)} kcal`, nameStr] as [string, string];
              return [`${value.toFixed(1)}g`, nameStr] as [string, string];
            }}
            labelStyle={{ color: '#374151' }}
          />
          <Legend />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="calories"
            stroke="#22c55e"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="Calories"
          />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="caloriesTarget"
            stroke="#22c55e"
            strokeWidth={1}
            strokeDasharray="5 5"
            dot={false}
            name="Calories Target"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="protein"
            stroke="#ef4444"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="Protein"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="proteinTarget"
            stroke="#ef4444"
            strokeWidth={1}
            strokeDasharray="5 5"
            dot={false}
            name="Protein Target"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="carbs"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="Carbs"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="carbsTarget"
            stroke="#3b82f6"
            strokeWidth={1}
            strokeDasharray="5 5"
            dot={false}
            name="Carbs Target"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="fat"
            stroke="#eab308"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="Fat"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="fatTarget"
            stroke="#eab308"
            strokeWidth={1}
            strokeDasharray="5 5"
            dot={false}
            name="Fat Target"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
