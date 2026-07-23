/**
 * Enhanced Activity Log Types
 * 
 * Designed to work with both current simple ActivityLog model
 * and future enhanced model with rich metadata
 */

import type { ActivityLog } from './index';

/**
 * Enhanced Activity Log with optional rich metadata
 * Backwards compatible with existing ActivityLog
 */
export interface EnhancedActivityLog extends ActivityLog {
  // Core fields (from existing model)
  id: string;
  job_id: string;
  action: string;
  description: string;
  created_at: string;
  
  // Enhanced fields (optional, future)
  previous_value?: string | null;
  new_value?: string | null;
  user_name?: string | null;
  user_id?: string | null;
  entity_type?: string | null;  // 'quotation', 'payment', 'measurement', etc.
  entity_id?: string | null;
  metadata?: Record<string, any> | null;
}

/**
 * Change comparison metadata
 */
export interface ChangeMetadata {
  field: string;
  previousValue: string;
  newValue: string;
  displayType?: 'text' | 'currency' | 'percentage' | 'date' | 'status';
}

/**
 * Event category for filtering and display
 */
export type EventCategory =
  | 'workflow'
  | 'quotation'
  | 'payments'
  | 'measurements'
  | 'notes'
  | 'documents'
  | 'other';

/**
 * Event configuration for display
 */
export interface EventConfig {
  icon: any;  // Lucide icon component
  color: string;
  category: EventCategory;
  expandable: boolean;
  navigable: boolean;
}

/**
 * Filter options for timeline
 */
export interface TimelineFilters {
  category?: EventCategory | 'all';
  dateFrom?: Date;
  dateTo?: Date;
  user?: string;
  entityType?: string;
  searchQuery?: string;
}

/**
 * Timeline statistics
 */
export interface TimelineStats {
  totalEvents: number;
  eventsByCategory: Record<EventCategory, number>;
  lastActivityDate: string | null;
  projectAge: number;  // in days
  currentStageDuration: number;  // in days
  delayedStages: number;
}
