import api from '../lib/api';
import type { Measurement, MeasurementItem, PaginatedResponse } from '../types';

export const measurementsApi = {
  // Measurements
  getJobMeasurements: async (jobId: string, params?: {
    limit?: number;
    offset?: number;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
  }) => {
    const { data } = await api.get<PaginatedResponse<Measurement>>(`/jobs/${jobId}/measurements`, { params });
    return data;
  },

  getById: async (id: string) => {
    const { data } = await api.get<Measurement>(`/measurements/${id}`);
    return data;
  },

  create: async (jobId: string, measurement: {
    visit_date?: string;
    measured_by?: string;
    notes?: string;
  }) => {
    const { data } = await api.post<Measurement>(`/jobs/${jobId}/measurements`, measurement);
    return data;
  },

  update: async (id: string, measurement: {
    visit_date?: string;
    measured_by?: string;
    notes?: string;
  }) => {
    const { data } = await api.put<Measurement>(`/measurements/${id}`, measurement);
    return data;
  },

  // Measurement Items
  getItems: async (measurementId: string) => {
    const { data } = await api.get<MeasurementItem[]>(`/measurements/${measurementId}/items`);
    return data;
  },

  addItem: async (measurementId: string, item: {
    quotation_item_id: string;
    room_name?: string;
    piece_number?: string;
    width?: string;
    height?: string;
    quantity: number;
    notes?: string;
  }) => {
    const { data } = await api.post<MeasurementItem>(`/measurements/${measurementId}/items`, item);
    return data;
  },

  updateItem: async (itemId: string, item: {
    quotation_item_id?: string;
    room_name?: string;
    piece_number?: string;
    width?: string;
    height?: string;
    quantity?: number;
    notes?: string;
  }) => {
    const { data } = await api.put<MeasurementItem>(`/measurement-items/${itemId}`, item);
    return data;
  },
};
