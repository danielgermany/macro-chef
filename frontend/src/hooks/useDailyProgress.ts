import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { mealService } from '../services/mealService';
import type { MealLog } from '../types/meal';

export function useDailyProgress(userId: number, date?: string) {
  return useQuery({
    queryKey: ['dailyProgress', userId, date],
    queryFn: () => mealService.getDailyProgress(userId, date),
    refetchInterval: 30000, // Refresh every 30 seconds
  });
}

export function useLogMeal(userId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (meal: Partial<MealLog>) => mealService.logMeal(userId, meal),
    onSuccess: () => {
      // Invalidate and refetch daily progress
      queryClient.invalidateQueries({ queryKey: ['dailyProgress', userId] });
    },
  });
}

export function useDeleteMeal(userId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (mealId: number) => mealService.deleteMeal(mealId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dailyProgress', userId] });
    },
  });
}

export function useMealRecommendations(
  userId: number,
  mealTime: string,
  enabled: boolean = true
) {
  return useQuery({
    queryKey: ['recommendations', userId, mealTime],
    queryFn: () => mealService.getRecommendations(userId, mealTime),
    enabled,
  });
}
