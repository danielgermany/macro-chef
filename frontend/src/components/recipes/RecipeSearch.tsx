import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { recipeService } from '../../services/recipeService';
import { RecipeDetailsModal } from './RecipeDetailsModal';
import { Search, Clock, Flame, Zap, Eye } from 'lucide-react';
import type { Recipe } from '../../services/recipeService';

interface RecipeSearchProps {
  userId: number;
  onSelectRecipe?: (recipe: Recipe) => void;
  maxResults?: number;
  showFilters?: boolean;
}

export function RecipeSearch({ userId, onSelectRecipe, maxResults = 10, showFilters = true }: RecipeSearchProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [maxCalories, setMaxCalories] = useState<number | undefined>();
  const [minProtein, setMinProtein] = useState<number | undefined>();
  const [maxReadyTime, setMaxReadyTime] = useState<number | undefined>();
  const [isSearching, setIsSearching] = useState(false);
  const [selectedRecipeId, setSelectedRecipeId] = useState<number | null>(null);

  const { data: recipes, isLoading } = useQuery({
    queryKey: ['recipes', userId, searchQuery, maxCalories, minProtein, maxReadyTime],
    queryFn: () =>
      recipeService.searchRecipes(userId, {
        query: searchQuery,
        max_results: maxResults,
        max_calories: maxCalories,
        min_protein: minProtein,
        max_ready_time: maxReadyTime,
      }),
    enabled: isSearching && searchQuery.length > 0,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim().length > 0) {
      setIsSearching(true);
    }
  };

  const handleSelectRecipe = (recipe: Recipe) => {
    if (onSelectRecipe) {
      onSelectRecipe(recipe);
    }
  };

  return (
    <div className="space-y-4">
      {/* Search Form */}
      <form onSubmit={handleSearch} className="space-y-3">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setIsSearching(false);
              }}
              placeholder="Search for recipes..."
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <button
            type="submit"
            disabled={!searchQuery.trim() || isLoading}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Max Calories
              </label>
              <input
                type="number"
                value={maxCalories || ''}
                onChange={(e) => setMaxCalories(e.target.value ? parseInt(e.target.value) : undefined)}
                placeholder="No limit"
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Min Protein (g)
              </label>
              <input
                type="number"
                value={minProtein || ''}
                onChange={(e) => setMinProtein(e.target.value ? parseInt(e.target.value) : undefined)}
                placeholder="No limit"
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Max Time (min)
              </label>
              <input
                type="number"
                value={maxReadyTime || ''}
                onChange={(e) => setMaxReadyTime(e.target.value ? parseInt(e.target.value) : undefined)}
                placeholder="No limit"
                min="1"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
              />
            </div>
          </div>
        )}
      </form>

      {/* Results */}
      {isSearching && (
        <div className="space-y-3">
          {isLoading ? (
            <div className="text-center py-8 text-gray-500">Searching recipes...</div>
          ) : recipes && recipes.length > 0 ? (
            <>
              <div className="text-sm text-gray-600">
                Found {recipes.length} recipe{recipes.length !== 1 ? 's' : ''}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {recipes.map((recipe) => (
                  <div
                    key={recipe.id}
                    className="bg-white border border-gray-200 rounded-lg p-4 hover:border-primary-300 hover:shadow-md transition-all"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-semibold text-gray-900">{recipe.title}</h3>
                      {recipe.is_validated && (
                        <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                          Validated
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <Flame className="w-4 h-4" />
                        <span>{recipe.nutrition.calories} kcal</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Zap className="w-4 h-4" />
                        <span>{recipe.nutrition.protein}g protein</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        <span>{recipe.readyInMinutes} min</span>
                      </div>
                    </div>
                    <div className="mt-2 text-xs text-gray-500 mb-3">
                      {recipe.nutrition.carbs}g carbs • {recipe.nutrition.fat}g fat
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleSelectRecipe(recipe)}
                        className="flex-1 px-3 py-1.5 bg-primary-600 text-white text-sm rounded-lg hover:bg-primary-700 transition-colors"
                      >
                        Use Recipe
                      </button>
                      <button
                        onClick={() => setSelectedRecipeId(recipe.id)}
                        className="px-3 py-1.5 bg-gray-200 text-gray-700 text-sm rounded-lg hover:bg-gray-300 transition-colors flex items-center gap-1"
                      >
                        <Eye className="w-4 h-4" />
                        Details
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No recipes found. Try a different search term.
            </div>
          )}
        </div>
      )}

      {/* Recipe Details Modal */}
      {selectedRecipeId && (
        <RecipeDetailsModal
          recipeId={selectedRecipeId}
          onClose={() => setSelectedRecipeId(null)}
        />
      )}
    </div>
  );
}
