import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { planService, type WeeklyPlan, type SavedPlan } from '../services/planService';

export function useWeeklyPlanner(userId: number) {
  const queryClient = useQueryClient();

  const generatePlanMutation = useMutation({
    mutationFn: (options?: {
      weekStart?: string;
      planName?: string;
      autoRecommend?: boolean;
    }) => planService.generatePlan(userId, options),
  });

  const savePlanMutation = useMutation({
    mutationFn: (plan: WeeklyPlan) => planService.savePlan(userId, plan),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['savedPlans', userId] });
    },
  });

  const savePlanWithCallbacks = (plan: WeeklyPlan, callbacks?: { onSuccess?: () => void; onError?: () => void }) => {
    savePlanMutation.mutate(plan, {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['savedPlans', userId] });
        callbacks?.onSuccess?.();
      },
      onError: () => {
        callbacks?.onError?.();
      },
    });
  };

  const savedPlansQuery = useQuery({
    queryKey: ['savedPlans', userId],
    queryFn: () => planService.getPlans(userId),
  });

  const planQuery = (planId: number) =>
    useQuery({
      queryKey: ['plan', planId],
      queryFn: () => planService.getPlan(planId),
      enabled: !!planId,
    });

  const shoppingListQuery = (planId: number) =>
    useQuery({
      queryKey: ['shoppingList', planId],
      queryFn: () => planService.getShoppingList(planId),
      enabled: !!planId,
    });

  return {
    generatePlan: generatePlanMutation.mutate,
    generatePlanAsync: generatePlanMutation.mutateAsync,
    isGenerating: generatePlanMutation.isPending,
    generatedPlan: generatePlanMutation.data,
    savePlan: savePlanWithCallbacks,
    isSaving: savePlanMutation.isPending,
    savedPlans: savedPlansQuery.data || [],
    isLoadingPlans: savedPlansQuery.isLoading,
    planQuery,
    shoppingListQuery,
  };
}
