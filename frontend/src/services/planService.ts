import { api } from './api';

export interface WeeklyPlan {
  plan_name?: string;
  week_start: string;
  week_end: string;
  daily_plans: DailyPlan[];
  total_cost_estimate: number;
}

export interface DailyPlan {
  date: string;
  day_name: string;
  meals: MealPlan[];
  daily_cost: number;
  daily_nutrition: {
    calories: number;
    protein_g: number;
    carbs_g: number;
    fat_g: number;
  };
}

export interface MealPlan {
  meal_time: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  meal_name: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  meal_template_id?: number;
  cost_estimate_usd?: number;
}

export interface SavedPlan {
  id: number;
  plan_name: string;
  week_start_date: string;
  week_end_date: string;
  total_cost_estimate_usd: number;
  created_at?: string;
}

export interface ShoppingList {
  items: ShoppingListItem[];
  total_estimated_cost: number;
  grouped_by_category: Record<string, ShoppingListItem[]>;
  grouped_by_store?: Record<string, ShoppingListItem[]>;
}

export interface ShoppingListItem {
  item_name: string;
  quantity: number;
  unit: string;
  category?: string;
  estimated_cost?: number;
}

export const planService = {
  async generatePlan(
    userId: number,
    options?: {
      weekStart?: string;
      planName?: string;
      autoRecommend?: boolean;
    }
  ): Promise<WeeklyPlan> {
    const response = await api.post(
      `/plans/generate?user_id=${userId}`,
      {
        week_start: options?.weekStart || null,
        plan_name: options?.planName || null,
        auto_recommend: options?.autoRecommend ?? true,
      }
    );
    return response.data;
  },

  async savePlan(userId: number, plan: WeeklyPlan): Promise<{ plan_id: number; message: string }> {
    const response = await api.post(`/plans?user_id=${userId}`, {
      plan,
    });
    return response.data;
  },

  async getPlans(userId: number, limit: number = 10): Promise<SavedPlan[]> {
    const response = await api.get(`/plans?user_id=${userId}&limit=${limit}`);
    return response.data;
  },

  async getPlan(planId: number): Promise<WeeklyPlan> {
    const response = await api.get(`/plans/${planId}`);
    return response.data;
  },

  async getShoppingList(planId: number): Promise<ShoppingList> {
    const response = await api.get(`/plans/${planId}/shopping-list`);
    return response.data;
  },
};
