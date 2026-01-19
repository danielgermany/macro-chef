import { Plus, Target, TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function QuickActions() {
  const navigate = useNavigate();

  const actions = [
    {
      icon: Plus,
      label: 'Log Meal',
      onClick: () => navigate('/meals'),
      color: 'bg-primary-500 hover:bg-primary-600',
    },
    {
      icon: Target,
      label: 'Generate Targets',
      onClick: () => navigate('/nutrition'),
      color: 'bg-blue-500 hover:bg-blue-600',
    },
    {
      icon: TrendingUp,
      label: 'View Progress',
      onClick: () => navigate('/nutrition'),
      color: 'bg-purple-500 hover:bg-purple-600',
    },
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
      <div className="space-y-3">
        {actions.map((action) => (
          <button
            key={action.label}
            onClick={action.onClick}
            className={`w-full flex items-center gap-3 px-4 py-3 ${action.color} text-white rounded-lg transition-colors`}
          >
            <action.icon className="w-5 h-5" />
            <span className="font-medium">{action.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
