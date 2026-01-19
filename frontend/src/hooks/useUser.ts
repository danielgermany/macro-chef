import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userService } from '../services/userService';
import type { User, BodyMetrics } from '../types/user';

export function useUser(userId: number) {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: () => userService.getUser(userId),
  });
}

export function useUpdateUser(userId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userData: Partial<User>) => userService.updateUser(userId, userData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user', userId] });
    },
  });
}

export function useLogBodyMetrics(userId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (metrics: Partial<BodyMetrics>) => userService.logBodyMetrics(userId, metrics),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['metrics', userId] });
      queryClient.invalidateQueries({ queryKey: ['user', userId] });
    },
  });
}

export function useMetricsHistory(userId: number, days: number = 30) {
  return useQuery({
    queryKey: ['metrics', userId, days],
    queryFn: () => userService.getMetricsHistory(userId, days),
  });
}

export function useProgressSummary(userId: number, days: number = 30) {
  return useQuery({
    queryKey: ['progress', userId, days],
    queryFn: () => userService.getProgressSummary(userId, days),
  });
}
