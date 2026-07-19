export interface Customer {
  id: string;
  full_name: string;
  phone_number: string;
  city?: string;
  address?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface ProductCategory {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: string;
  category_id: string;
  name: string;
  description?: string;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface QuotationItem {
  id: string;
  quotation_id: string;
  product_id: string;
  quantity: number;
  unit_price: string;
  total_price: string;
  description?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Quotation {
  id: string;
  quotation_number: string;
  customer_id: string;
  quotation_date: string;
  status: QuotationStatus;
  total_price: string;
  discount: string;
  final_price: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  items?: QuotationItem[];
}

export type QuotationStatus =
  | 'draft'
  | 'waiting_for_measurement'
  | 'measured'
  | 'under_negotiation'
  | 'sent'
  | 'approved'
  | 'rejected'
  | 'cancelled'
  | 'expired';

export interface Job {
  id: string;
  job_number: string;
  quotation_id?: string;
  customer_id: string;
  start_date?: string;
  end_date?: string;
  status: JobStatus;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export type JobStatus =
  | 'pending'
  | 'in_progress'
  | 'completed'
  | 'cancelled';

export interface Payment {
  id: string;
  quotation_id?: string;
  job_id?: string;
  customer_id: string;
  amount: string;
  payment_date: string;
  payment_method: PaymentMethod;
  reference_number?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export type PaymentMethod =
  | 'cash'
  | 'bank_transfer'
  | 'check'
  | 'credit_card';

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}
