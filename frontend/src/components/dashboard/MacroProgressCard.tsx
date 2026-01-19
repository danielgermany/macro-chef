interface MacroProgressCardProps {
  label: string;
  current: number;
  target: number;
  unit: string;
  color: string;
}

export function MacroProgressCard({
  label,
  current,
  target,
  unit,
  color,
}: MacroProgressCardProps) {
  const percentage = Math.min((current / target) * 100, 100);
  const remaining = target - current;
  const isOver = current > target;

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className="text-2xl font-bold">
            {current.toFixed(0)}
            <span className="text-sm font-normal text-gray-400 ml-1">
              / {target} {unit}
            </span>
          </p>
        </div>
        <span
          className={`text-sm font-medium px-2 py-1 rounded-full ${
            isOver
              ? 'bg-red-100 text-red-600'
              : 'bg-green-100 text-green-600'
          }`}
        >
          {isOver ? `+${Math.abs(remaining).toFixed(0)}` : remaining.toFixed(0)} left
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-3">
        <div
          className={`h-3 rounded-full transition-all duration-500 ${color} ${
            isOver ? 'bg-red-500' : ''
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      <p className="text-xs text-gray-400 mt-2 text-right">
        {percentage.toFixed(0)}%
      </p>
    </div>
  );
}
