import { useAuth } from '../../contexts/AuthContext';
import { LogOut, User } from 'lucide-react';

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-800">Macro Chef</h2>
        <div className="flex items-center space-x-4">
          {user && (
            <>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <User className="w-4 h-4" />
                <span>{user.name}</span>
              </div>
              <button
                onClick={logout}
                className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
