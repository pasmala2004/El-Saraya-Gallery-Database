/**
 * Dashboard types matching backend DTOs
 */

export interface PaymentProgress {
  paid: string;
  total: string;
  percentage: string;
}

export interface JobPipelineCard {
  job_id: string;
  job_number: string;
  quotation_number: string;
  customer_name: string;
  current_status: string;
  assigned_engineer: string | null;
  last_activity: string;
  days_in_stage: number;
  payment_progress: PaymentProgress;
  priority: 'high' | 'medium' | 'low';
  measurement_date: string | null;
  installation_date: string | null;
  is_overdue: boolean;
  created_at: string;
  updated_at: string;
}

export interface Pipeline {
  quotation: JobPipelineCard[];
  measurement: JobPipelineCard[];
  depositReceived: JobPipelineCard[];
  manufacturing: JobPipelineCard[];
  installation: JobPipelineCard[];
  completed: JobPipelineCard[];
  rejected: JobPipelineCard[];
}

export interface KPIs {
  total_active_jobs: number;
  quotations_waiting_response: number;
  measurements_scheduled_today: number;
  installations_scheduled_today: number;
  overdue_payments: number;
  jobs_delayed: number;
}

export interface Alert {
  id: string;
  type: string;
  severity: 'critical' | 'warning' | 'info';
  title: string;
  description: string;
  entity_id: string;
  entity_type: 'job' | 'quotation' | 'payment';
  days_overdue: number;
}

export interface Activity {
  id: string;
  type: string;
  description: string;
  timestamp: string;
  relative_time: string;
  entity_id: string;
  entity_type: string;
  customer_name: string;
}

export interface DashboardMetadata {
  generated_at: string;
  execution_time_ms: number;
}

export interface DashboardData {
  kpis: KPIs;
  pipeline: Pipeline;
  alerts: Alert[];
  recentActivity: Activity[];
  metadata: DashboardMetadata;
}
