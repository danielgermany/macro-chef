import { useAuth } from '../contexts/AuthContext';
import { RecipeSearch } from '../components/recipes/RecipeSearch';
import { Search } from 'lucide-react';

export function Recipes() {
  const { user: authUser } = useAuth();
  const userId = authUser?.id || 1;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Search className="w-8 h-8 text-primary-600" />
        <h1 className="text-3xl font-bold text-gray-900">Recipe Search</h1>
      </div>
      
      <div className="bg-white rounded-xl shadow-sm p-6">
        <p className="text-gray-600 mb-4">
          Search through 570,000+ recipes from Spoonacular. Find recipes that match your nutrition goals,
          dietary restrictions, and cooking preferences.
        </p>
        <RecipeSearch userId={userId} maxResults={12} showFilters={true} />
      </div>
    </div>
  );
}
