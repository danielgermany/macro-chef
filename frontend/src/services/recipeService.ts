import { api } from './api';

export interface RecipeSearchParams {
  query: string;
  max_results?: number;
  max_calories?: number;
  min_protein?: number;
  max_ready_time?: number;
}

export interface Recipe {
  id: number;
  title: string;
  readyInMinutes: number;
  nutrition: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
  };
  is_validated?: boolean;
  api_recipe_id?: string;
}

export interface RecipeDetails {
  id: number;
  title: string;
  readyInMinutes: number;
  servings: number;
  image?: string;
  sourceUrl?: string;
  spoonacularSourceUrl?: string;
  vegetarian?: boolean;
  vegan?: boolean;
  glutenFree?: boolean;
  nutrition?: {
    nutrients: Array<{
      name: string;
      amount: number;
      unit: string;
    }>;
  };
  extendedIngredients?: Array<{
    name: string;
    amount: number;
    unit: string;
  }>;
  analyzedInstructions?: Array<{
    steps: Array<{
      step: string;
    }>;
  }>;
}

export const recipeService = {
  async searchRecipes(
    userId: number,
    params: RecipeSearchParams
  ): Promise<Recipe[]> {
    const searchParams = new URLSearchParams({
      user_id: String(userId),
      query: params.query,
      max_results: String(params.max_results || 10),
    });
    
    if (params.max_calories) {
      searchParams.append('max_calories', String(params.max_calories));
    }
    if (params.min_protein) {
      searchParams.append('min_protein', String(params.min_protein));
    }
    if (params.max_ready_time) {
      searchParams.append('max_ready_time', String(params.max_ready_time));
    }

    const response = await api.get(`/recipes/search?${searchParams}`);
    return response.data;
  },

  async getRecipeDetails(recipeId: number): Promise<RecipeDetails> {
    const response = await api.get(`/recipes/${recipeId}`);
    return response.data;
  },
};
