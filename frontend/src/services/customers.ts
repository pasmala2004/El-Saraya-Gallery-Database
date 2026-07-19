import api from '../lib/api';
import { Customer, PaginatedResponse } from '../types';

export const customersApi = {
  getAll: async (params?: {
    limit?: number;
    offset?: number;
    name?: string;
    city?: string;
  }) => {
    const { data } = await api.get<PaginatedResponse<Customer>>('/customers', { params });
    return data;
  },

  getById: async (id: string) => {
    const { data } = await api.get<Customer>(`/customers/${id}`);
    return data;
  },

  create: async (customer: Partial<Customer>) => {
    const { data } = await api.post<Customer>('/customers', customer);
    return data;
  },

  update: async (id: string, customer: Partial<Customer>) => {
    const { data} = await api.put<Customer>(`/customers/${id}`, customer);
    return data;
  },

  delete: async (id: string) => {
    await api.delete(`/customers/${id}`);
  },
};
