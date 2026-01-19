import { useQuery } from '@tanstack/react-query';
import { userService } from '../../services/userService';
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
import { format, parseISO, subDays } from 'date-fns';

interface WeightChartProps {
  userId: number;
  days?: number;
}

export function WeightChart({ userId, days = 30 }: WeightChartProps) {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['metrics', userId, days],
    queryFn: () => userService.getMetricsHistory(userId, days),
  });

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">Weight Progress</h2>
        <div className="h-64 flex items-center justify-center text-gray-500">
          Loading weight data...
        </div>
      </div>
    );
  }

  if (!metrics || metrics.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">Weight Progress</h2>
        <div className="h-64 flex items-center justify-center text-gray-500">
          No weight data available. Log body metrics in Settings to track your progress.
        </div>
      </div>
    );
  }

  // Prepare chart data
  const chartData = metrics
    .map((metric) => ({
      date: format(parseISO(metric.date), 'MMM d'),
      dateFull: metric.date,
      weight: metric.weight_lbs,
      bodyFat: metric.body_fat_pct,
      muscle: metric.muscle_mass_lbs,
    }))
    .sort((a, b) => new Date(a.dateFull).getTime() - new Date(b.dateFull).getTime());

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <h2 className="text-xl font-semibold mb-4">Weight Progress</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis yAxisId="left" label={{ value: 'Weight (lbs)', angle: -90, position: 'insideLeft' }} />
          {chartData.some((d) => d.bodyFat != null) && (
            <YAxis
              yAxisId="right"
              orientation="right"
              label={{ value: 'Body Fat (%)', angle: 90, position: 'insideRight' }}
            />
          )}
          <Tooltip
            formatter={(value: number, name: string) => {
              if (name === 'weight') return [`${value.toFixed(1)} lbs`, 'Weight'];
              if (name === 'bodyFat') return [`${value.toFixed(1)}%`, 'Body Fat'];
              if (name === 'muscle') return [`${value.toFixed(1)} lbs`, 'Muscle'];
              return [value, name];
            }}
            labelStyle={{ color: '#374151' }}
          />
          <Legend />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="weight"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="Weight"
          />
          {chartData.some((d) => d.bodyFat != null) && (
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="bodyFat"
              stroke="#ef4444"
              strokeWidth={2}
              dot={{ r: 4 }}
              name="Body Fat %"
            />
          )}
          {chartData.some((d) => d.muscle != null) && (
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="muscle"
              stroke="#22c55e"
              strokeWidth={2}
              dot={{ r: 4 }}
              name="Muscle Mass"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
