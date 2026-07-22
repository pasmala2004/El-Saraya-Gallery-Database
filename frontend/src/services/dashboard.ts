import api from '../lib/api';
import type { DashboardData } from '../types/dashboard';

export const dashboardApi = {
  /**
   * Get aggregated dashboard data
   * 
   * Returns KPIs, pipeline, alerts, and recent activity in a single request.
   * Target response time: <500ms
   */
  getDashboard: async (): Promise<DashboardData> => {
    const { data } = await api.get<DashboardData>('/dashboard');
    return data;
  },
};
