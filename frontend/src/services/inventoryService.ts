import { api } from './api';

export interface InventoryItem {
  id: number;
  user_id: number;
  item_name: string;
  quantity: number;
  unit: string;
  category?: string;
  location?: string;
  expiration_date?: string;
  purchase_date?: string;
  notes?: string;
}

export const inventoryService = {
  async getItems(userId: number, location?: string, category?: string): Promise<InventoryItem[]> {
    const params = new URLSearchParams({ user_id: String(userId) });
    if (location) params.append('location', location);
    if (category) params.append('category', category);
    const response = await api.get(`/inventory?${params}`);
    return response.data;
  },

  async addItem(userId: number, item: Partial<InventoryItem>): Promise<InventoryItem> {
    const response = await api.post(`/inventory?user_id=${userId}`, item);
    return response.data;
  },

  async getItem(itemId: number): Promise<InventoryItem> {
    const response = await api.get(`/inventory/${itemId}`);
    return response.data;
  },

  async updateItem(itemId: number, item: Partial<InventoryItem>): Promise<InventoryItem> {
    const response = await api.patch(`/inventory/${itemId}`, item);
    return response.data;
  },

  async deleteItem(itemId: number): Promise<void> {
    await api.delete(`/inventory/${itemId}`);
  },

  async useItem(itemId: number, quantity: number): Promise<void> {
    await api.post(`/inventory/${itemId}/use?quantity=${quantity}`);
  },

  async getExpiringItems(userId: number, days: number = 7): Promise<InventoryItem[]> {
    const response = await api.get(`/inventory/expiring?user_id=${userId}&days=${days}`);
    return response.data;
  },
};
