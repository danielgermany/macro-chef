import { api } from './api';
import type { NutritionTargets } from '../types/meal';

export const nutritionService = {
  async generateTargets(userId: number, targetDate?: string, isTrainingDay?: boolean): Promise<NutritionTargets> {
    const response = await api.post('/nutrition/targets', {
      user_id: userId,
      target_date: targetDate,
      is_training_day: isTrainingDay || false,
    });
    return response.data;
  },

  async getTodayTargets(userId: number): Promise<NutritionTargets> {
    const response = await api.get(`/nutrition/targets?user_id=${userId}`);
    return response.data;
  },

  async getTargetsForDate(userId: number, date: string): Promise<NutritionTargets> {
    const response = await api.get(`/nutrition/targets/${date}?user_id=${userId}`);
    return response.data;
  },
};
