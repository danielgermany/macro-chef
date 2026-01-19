import { api } from './api';
import type { MealLog, DailyProgress, MealRecommendation } from '../types/meal';

export const mealService = {
  async logMeal(userId: number, meal: Partial<MealLog>): Promise<MealLog> {
    const response = await api.post(`/meals/log?user_id=${userId}`, meal);
    return response.data;
  },

  async getDailyProgress(userId: number, date?: string): Promise<DailyProgress> {
    const params = new URLSearchParams({ user_id: String(userId) });
    if (date) params.append('target_date', date);
    const response = await api.get(`/meals/progress?${params}`);
    return response.data;
  },

  async getMealHistory(
    userId: number,
    options?: {
      days?: number;
      startDate?: string;
      endDate?: string;
      mealName?: string;
    }
  ): Promise<MealLog[]> {
    const params = new URLSearchParams({ user_id: String(userId) });
    if (options?.days) params.append('days', String(options.days));
    if (options?.startDate) params.append('start_date', options.startDate);
    if (options?.endDate) params.append('end_date', options.endDate);
    if (options?.mealName) params.append('meal_name', options.mealName);
    const response = await api.get(`/meals/history?${params.toString()}`);
    return response.data;
  },

  async deleteMeal(mealId: number): Promise<void> {
    await api.delete(`/meals/${mealId}`);
  },

  async updateMealRating(mealId: number, rating: number): Promise<void> {
    await api.patch(`/meals/${mealId}/rating?rating=${rating}`);
  },

  async getRecommendations(
    userId: number,
    mealTime: string,
    options?: { maxTime?: number; budgetLimit?: number }
  ): Promise<MealRecommendation[]> {
    const params = new URLSearchParams({
      user_id: String(userId),
      meal_time: mealTime,
    });
    if (options?.maxTime) params.append('max_time', String(options.maxTime));
    if (options?.budgetLimit) params.append('budget_limit', String(options.budgetLimit));
    
    const response = await api.get(`/meals/recommendations?${params}`);
    return response.data;
  },
};
