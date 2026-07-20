import api from '../lib/api';
import type { Job, PaginatedResponse } from '../types';

export const jobsApi = {
  getAll: async (params?: {
    limit?: number;
    offset?: number;
    status?: string;
    customer?: string;
    quotation?: string;
    created_after?: string;
    created_before?: string;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
  }) => {
    const { data } = await api.get<PaginatedResponse<Job>>('/jobs', { params });
    return data;
  },

  getById: async (id: string) => {
    const { data } = await api.get<Job>(`/jobs/${id}`);
    return data;
  },

  getByQuotation: async (quotationId: string) => {
    const { data } = await api.get<Job>(`/quotations/${quotationId}/job`);
    return data;
  },

  create: async (job: { quotation_id: string; notes?: string }) => {
    const { data } = await api.post<Job>('/jobs', job);
    return data;
  },

  update: async (id: string, job: Partial<Job>) => {
    const { data } = await api.put<Job>(`/jobs/${id}`, job);
    return data;
  },

  updateStatus: async (id: string, status: string) => {
    const { data } = await api.patch<Job>(`/jobs/${id}/status`, { status });
    return data;
  },

  getCustomerJobs: async (customerId: string, params?: {
    limit?: number;
    offset?: number;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
  }) => {
    const { data } = await api.get<PaginatedResponse<Job>>(`/customers/${customerId}/jobs`, { params });
    return data;
  },
};
