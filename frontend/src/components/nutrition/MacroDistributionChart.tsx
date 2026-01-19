import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface MacroDistributionChartProps {
  protein: number;
  carbs: number;
  fat: number;
}

const COLORS = ['#ef4444', '#3b82f6', '#eab308'];

export function MacroDistributionChart({ protein, carbs, fat }: MacroDistributionChartProps) {
  const total = protein + carbs + fat;
  
  if (total === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Macro Distribution</h3>
        <div className="h-64 flex items-center justify-center text-gray-500">
          No macros logged yet
        </div>
      </div>
    );
  }

  const data = [
    { name: 'Protein', value: protein, percentage: ((protein / total) * 100).toFixed(1) },
    { name: 'Carbs', value: carbs, percentage: ((carbs / total) * 100).toFixed(1) },
    { name: 'Fat', value: fat, percentage: ((fat / total) * 100).toFixed(1) },
  ];

  // Calculate calories from macros (4 cal/g protein, 4 cal/g carbs, 9 cal/g fat)
  const caloriesFromMacros = (protein * 4) + (carbs * 4) + (fat * 9);

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <h3 className="text-lg font-semibold mb-4">Macro Distribution</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percentage }) => `${name} ${percentage}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => `${value.toFixed(1)}g`} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="space-y-4">
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Macro Breakdown</h4>
            <div className="space-y-2">
              {data.map((item, index) => (
                <div key={item.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-4 h-4 rounded"
                      style={{ backgroundColor: COLORS[index] }}
                    />
                    <span className="text-sm font-medium">{item.name}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-semibold">{item.value.toFixed(1)}g</span>
                    <span className="text-xs text-gray-500 ml-2">({item.percentage}%)</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="pt-4 border-t border-gray-200">
            <div className="text-sm text-gray-600">
              <div className="flex justify-between mb-1">
                <span>Total Macros:</span>
                <span className="font-medium">{total.toFixed(1)}g</span>
              </div>
              <div className="flex justify-between">
                <span>Calories from Macros:</span>
                <span className="font-medium">{caloriesFromMacros.toFixed(0)} kcal</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
