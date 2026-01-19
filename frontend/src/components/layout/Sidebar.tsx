import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  UtensilsCrossed,
  Apple,
  Package,
  Calendar,
  DollarSign,
  Settings,
} from 'lucide-react';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/meals', icon: UtensilsCrossed, label: 'Meal Tracker' },
  { path: '/nutrition', icon: Apple, label: 'Nutrition' },
  { path: '/inventory', icon: Package, label: 'Inventory' },
  { path: '/planner', icon: Calendar, label: 'Weekly Planner' },
  { path: '/budget', icon: DollarSign, label: 'Budget' },
];

export function Sidebar() {
  return (
    <aside className="w-64 bg-white shadow-md">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-primary-600">🍳 Macro Chef</h1>
      </div>
      <nav className="mt-6">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center px-6 py-3 text-gray-700 hover:bg-primary-50 hover:text-primary-600 transition-colors ${
                isActive ? 'bg-primary-50 text-primary-600 border-r-4 border-primary-600' : ''
              }`
            }
          >
            <item.icon className="w-5 h-5 mr-3" />
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="absolute bottom-0 w-64 p-6">
        <NavLink
          to="/settings"
          className="flex items-center text-gray-500 hover:text-gray-700"
        >
          <Settings className="w-5 h-5 mr-3" />
          Settings
        </NavLink>
      </div>
    </aside>
  );
}
