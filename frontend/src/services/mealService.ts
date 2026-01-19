import { api } from './api';
import type { MealLog, DailyProgress, MealRecommendation } from '../types/meal';

export const mealService = {
  async logMeal(userId: number, meal: Partial<MealLog>): Promise<MealLog> {
    const response = await api.post(`/meals/log?user_id=${userId}`, meal);
    return response.data;
  },

  async getDailyProgress(userId: number, date?: string): Promise<DailyProgress> {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/6ab49e72-b272-4456-a3cc-16544060033b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'mealService.ts:10',message:'getDailyProgress called',data:{userId,date},"timestamp":Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'F'})}).catch(()=>{});
    // #endregion
    const params = new URLSearchParams({ user_id: String(userId) });
    if (date) params.append('target_date', date);
    const url = `/meals/progress?${params.toString()}`;
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/6ab49e72-b272-4456-a3cc-16544060033b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'mealService.ts:14',message:'API request URL',data:{url,userId},"timestamp":Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
    // #endregion
    const response = await api.get(url);
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/6ab49e72-b272-4456-a3cc-16544060033b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'mealService.ts:16',message:'getDailyProgress response',data:{hasData:!!response.data,hasTotals:!!response.data?.totals,status:response.status},"timestamp":Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'F'})}).catch(()=>{});
    // #endregion
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
