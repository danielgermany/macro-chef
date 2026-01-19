import { useQuery } from '@tanstack/react-query';
import { recipeService } from '../../services/recipeService';
import { X, Clock, Users, ExternalLink, CheckCircle, AlertCircle } from 'lucide-react';

interface RecipeDetailsModalProps {
  recipeId: number;
  onClose: () => void;
}

export function RecipeDetailsModal({ recipeId, onClose }: RecipeDetailsModalProps) {
  const { data: recipe, isLoading } = useQuery({
    queryKey: ['recipe', recipeId],
    queryFn: () => recipeService.getRecipeDetails(recipeId),
    enabled: !!recipeId,
  });

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl shadow-lg max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
          <div className="p-6">
            <div className="animate-pulse space-y-4">
              <div className="h-8 bg-gray-200 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              <div className="h-64 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!recipe) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl shadow-lg max-w-3xl w-full mx-4 p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Recipe Not Found</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
          <p className="text-gray-600">The recipe could not be loaded.</p>
        </div>
      </div>
    );
  }

  const nutrition = recipe.nutrition || {};
  const nutrients = nutrition.nutrients || [];
  const nutrientsMap: Record<string, { amount: number; unit: string }> = {};
  nutrients.forEach((n: any) => {
    nutrientsMap[n.name.toLowerCase()] = { amount: n.amount, unit: n.unit || '' };
  });

  const extendedIngredients = recipe.extendedIngredients || [];
  const instructions = recipe.analyzedInstructions?.[0]?.steps || [];
  const sourceUrl = recipe.sourceUrl || recipe.spoonacularSourceUrl;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-start">
          <div className="flex-1">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">{recipe.title}</h2>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                <span>{recipe.readyInMinutes || 'N/A'} minutes</span>
              </div>
              <div className="flex items-center gap-1">
                <Users className="w-4 h-4" />
                <span>{recipe.servings || 'N/A'} servings</span>
              </div>
              {recipe.vegetarian && (
                <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">Vegetarian</span>
              )}
              {recipe.vegan && (
                <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">Vegan</span>
              )}
              {recipe.glutenFree && (
                <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">Gluten Free</span>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Image */}
          {recipe.image && (
            <div className="w-full h-64 rounded-lg overflow-hidden">
              <img
                src={recipe.image}
                alt={recipe.title}
                className="w-full h-full object-cover"
              />
            </div>
          )}

          {/* Nutrition Summary */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold mb-3">Nutrition (per serving)</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-gray-600">Calories</div>
                <div className="text-xl font-bold">
                  {nutrientsMap.calories?.amount.toFixed(0) || 'N/A'}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Protein</div>
                <div className="text-xl font-bold text-red-600">
                  {nutrientsMap.protein?.amount.toFixed(1) || 'N/A'}g
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Carbs</div>
                <div className="text-xl font-bold text-blue-600">
                  {nutrientsMap.carbohydrates?.amount.toFixed(1) || 'N/A'}g
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Fat</div>
                <div className="text-xl font-bold text-yellow-600">
                  {nutrientsMap.fat?.amount.toFixed(1) || 'N/A'}g
                </div>
              </div>
            </div>
          </div>

          {/* Ingredients */}
          {extendedIngredients.length > 0 && (
            <div>
              <h3 className="text-xl font-semibold mb-3">Ingredients</h3>
              <ul className="space-y-2">
                {extendedIngredients.map((ingredient: any, index: number) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-primary-600 mt-1">•</span>
                    <span>
                      <span className="font-medium">
                        {ingredient.amount} {ingredient.unit}
                      </span>{' '}
                      {ingredient.name}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Instructions */}
          {instructions.length > 0 && (
            <div>
              <h3 className="text-xl font-semibold mb-3">Instructions</h3>
              <ol className="space-y-3">
                {instructions.map((step: any, index: number) => (
                  <li key={index} className="flex gap-3">
                    <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-semibold">
                      {index + 1}
                    </span>
                    <span className="flex-1 pt-1">{step.step}</span>
                  </li>
                ))}
              </ol>
            </div>
          )}

          {/* Source Link */}
          {sourceUrl && (
            <div className="pt-4 border-t border-gray-200">
              <a
                href={sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium"
              >
                <ExternalLink className="w-4 h-4" />
                View Original Recipe
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
