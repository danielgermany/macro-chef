export interface User {
  id: number;
  name: string;
  age: number;
  sex: 'male' | 'female';
  height_inches: number;
  weight_lbs: number;
  body_fat_pct?: number;
  muscle_mass_lbs?: number;
  goal_type: 'bulk' | 'cut' | 'maintain' | 'recomp';
  activity_level: 'sedentary' | 'light' | 'moderate' | 'very_active' | 'athlete';
  training_days_per_week: number;
  cooking_skill: 'beginner' | 'intermediate' | 'advanced';
  cooking_frequency?: string;
  dietary_restrictions: string[];
  food_dislikes: string[];
  weekly_budget_usd: number;
  available_equipment: string[];
}

export interface BodyMetrics {
  id: number;
  user_id: number;
  date: string;
  weight_lbs: number;
  body_fat_pct?: number;
  muscle_mass_lbs?: number;
  waist_inches?: number;
  chest_inches?: number;
  arms_inches?: number;
  legs_inches?: number;
  notes?: string;
}

export interface ProgressSummary {
  status: string;
  period_days?: number;
  measurements_count?: number;
  starting_weight?: number;
  current_weight?: number;
  weight_change_lbs?: number;
  weight_change_pct?: number;
  starting_bodyfat?: number;
  current_bodyfat?: number;
  bodyfat_change_pct?: number;
  muscle_change_lbs?: number;
  message?: string;
}
