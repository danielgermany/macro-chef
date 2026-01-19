import { api } from './api';
import type { User, BodyMetrics, ProgressSummary } from '../types/user';

export const userService = {
  async createUser(userData: Partial<User>): Promise<User> {
    const response = await api.post('/users/', userData);
    return response.data;
  },

  async getUser(userId: number): Promise<User> {
    const response = await api.get(`/users/${userId}`);
    return response.data;
  },

  async updateUser(userId: number, userData: Partial<User>): Promise<User> {
    const response = await api.patch(`/users/${userId}`, userData);
    return response.data;
  },

  async logBodyMetrics(userId: number, metrics: Partial<BodyMetrics>): Promise<BodyMetrics> {
    const response = await api.post(`/users/${userId}/metrics`, metrics);
    return response.data;
  },

  async getMetricsHistory(userId: number, days: number = 30): Promise<BodyMetrics[]> {
    const response = await api.get(`/users/${userId}/metrics?days=${days}`);
    return response.data;
  },

  async getProgressSummary(userId: number, days: number = 30): Promise<ProgressSummary> {
    const response = await api.get(`/users/${userId}/progress?days=${days}`);
    return response.data;
  },

  async changePassword(currentPassword: string, newPassword: string): Promise<{ message: string }> {
    const response = await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  },

  async changeEmail(newEmail: string, password: string): Promise<{ message: string; new_email: string }> {
    const response = await api.post('/auth/change-email', {
      new_email: newEmail,
      password: password,
    });
    return response.data;
  },
};
