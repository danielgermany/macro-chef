export type MealTime = 'breakfast' | 'lunch' | 'dinner' | 'snack';

export interface MealLog {
  id: number;
  user_id: number;
  date: string;
  meal_time: MealTime;
  meal_name: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g?: number;
  sugar_g?: number;
  saturated_fat_g?: number;
  sodium_mg?: number;
  cholesterol_mg?: number;
  serving_size?: string;
  notes?: string;
  rating?: number;
  logged_at?: string;
}

export interface NutritionTotals {
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
  sugar_g: number;
  saturated_fat_g: number;
  sodium_mg: number;
  cholesterol_mg: number;
}

export interface NutritionTargets {
  calories_target: number;
  protein_target_g: number;
  carbs_target_g: number;
  fat_target_g: number;
  fiber_target_g?: number;
  sugar_limit_g?: number;
  saturated_fat_limit_g?: number;
  sodium_limit_mg?: number;
  cholesterol_limit_mg?: number;
}

export interface DailyProgress {
  date: string;
  meals: MealLog[];
  meal_count: number;
  totals: NutritionTotals;
  targets: NutritionTargets;
  remaining: {
    calories: number;
    protein_g: number;
    carbs_g: number;
    fat_g: number;
    fiber_g: number;
  };
  percentages: {
    calories: number;
    protein_g: number;
    carbs_g: number;
    fat_g: number;
  };
}

export interface MealRecommendation {
  id?: number;
  name: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  total_time_minutes?: number;
  difficulty?: string;
  cost_estimate_usd?: number;
  recommendation_score: number;
  match_reasons: string[];
  is_online_recipe: boolean;
  api_recipe_id?: string;
  nutrition_validated?: boolean;
}
