import { useQuery } from '@tanstack/react-query';
import { budgetService, type BudgetSummary, type SpendingTrend, type CategoryBreakdown } from '../services/budgetService';

export function useBudget(userId: number) {
  const weeklySummary = useQuery({
    queryKey: ['budget', 'weekly', userId],
    queryFn: () => budgetService.getWeeklySummary(userId),
  });

  const monthlySummary = useQuery({
    queryKey: ['budget', 'monthly', userId],
    queryFn: () => budgetService.getMonthlySummary(userId),
  });

  const spendingTrends = useQuery({
    queryKey: ['budget', 'trends', userId],
    queryFn: () => budgetService.getSpendingTrends(userId, 30),
  });

  const categoryBreakdown = useQuery({
    queryKey: ['budget', 'categories', userId],
    queryFn: () => budgetService.getCategoryBreakdown(userId, 30),
  });

  return {
    weeklySummary: weeklySummary.data,
    isLoadingWeekly: weeklySummary.isLoading,
    monthlySummary: monthlySummary.data,
    isLoadingMonthly: monthlySummary.isLoading,
    spendingTrends: spendingTrends.data,
    isLoadingTrends: spendingTrends.isLoading,
    categoryBreakdown: categoryBreakdown.data || [],
    isLoadingCategories: categoryBreakdown.isLoading,
  };
}
