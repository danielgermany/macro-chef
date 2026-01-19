import { api } from './api';

export interface BudgetSummary {
  period_start: string;
  period_end: string;
  total_spent: number;
  budget_limit: number;
  remaining: number;
  percentage_used: number;
  daily_average: number;
  category_breakdown: Record<string, number>;
  trend?: string;
  // Additional fields from backend
  num_trips?: number;
  num_items?: number;
  avg_per_trip?: number;
  is_over_budget?: boolean;
  period_type?: 'weekly' | 'monthly';
}

export interface SpendingTrend {
  period: string;
  data_points: SpendingDataPoint[];
  trend_direction: string;
  average_change?: number;
  // Additional fields from backend
  weeks_analyzed?: number;
  weekly_data?: WeeklySpending[];
  avg_weekly_spending?: number;
  weekly_budget?: number;
  avg_over_under?: number;
  is_trending_over?: boolean;
}

export interface SpendingDataPoint {
  date: string;
  amount: number;
}

export interface WeeklySpending {
  week_start: string;
  week_end: string;
  total_spent: number;
  num_trips: number;
}

export interface CategoryBreakdown {
  category: string;
  num_items: number;
  total_spent: number;
  avg_item_price: number;
  percent_of_total: number;
}

export const budgetService = {
  async getWeeklySummary(
    userId: number,
    weekStart?: string
  ): Promise<BudgetSummary> {
    const params = new URLSearchParams({ user_id: String(userId) });
    if (weekStart) params.append('week_start', weekStart);
    const response = await api.get(`/budget/weekly?${params}`);
    return response.data;
  },

  async getMonthlySummary(
    userId: number,
    month?: number,
    year?: number
  ): Promise<BudgetSummary> {
    const params = new URLSearchParams({ user_id: String(userId) });
    if (month) params.append('month', String(month));
    if (year) params.append('year', String(year));
    const response = await api.get(`/budget/monthly?${params}`);
    return response.data;
  },

  async getSpendingTrends(
    userId: number,
    days: number = 30
  ): Promise<SpendingTrend> {
    const response = await api.get(
      `/budget/trends?user_id=${userId}&days=${days}`
    );
    return response.data;
  },

  async getCategoryBreakdown(
    userId: number,
    days: number = 30
  ): Promise<CategoryBreakdown[]> {
    const response = await api.get(
      `/budget/categories?user_id=${userId}&days=${days}`
    );
    return response.data;
  },
};
