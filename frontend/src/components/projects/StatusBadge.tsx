import { memo } from 'react';
import type { JobStatus, QuotationStatus } from '../../types';

interface StatusBadgeProps {
  status: JobStatus | QuotationStatus;
  size?: 'sm' | 'md' | 'lg';
  label: string;
}

const statusColors: Record<JobStatus | QuotationStatus, string> = {
  // Job statuses
  pending: 'bg-gray-100 text-gray-800 border-gray-300',
  measuring: 'bg-purple-100 text-purple-800 border-purple-300',
  in_production: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  ready_for_installation: 'bg-indigo-100 text-indigo-800 border-indigo-300',
  installed: 'bg-blue-100 text-blue-800 border-blue-300',
  completed: 'bg-green-100 text-green-800 border-green-300',
  cancelled: 'bg-red-100 text-red-800 border-red-300',
  // Quotation statuses
  draft: 'bg-gray-100 text-gray-800 border-gray-300',
  waiting_for_measurement: 'bg-blue-100 text-blue-800 border-blue-300',
  measured: 'bg-purple-100 text-purple-800 border-purple-300',
  under_negotiation: 'bg-orange-100 text-orange-800 border-orange-300',
  sent: 'bg-blue-100 text-blue-800 border-blue-300',
  approved: 'bg-green-100 text-green-800 border-green-300',
  rejected: 'bg-red-100 text-red-800 border-red-300',
  expired: 'bg-gray-100 text-gray-800 border-gray-300',
};

const sizeClasses = {
  sm: 'text-xs px-2 py-0.5',
  md: 'text-sm px-2.5 py-1',
  lg: 'text-base px-3 py-1.5',
};

function StatusBadge({ status, size = 'md', label }: StatusBadgeProps) {
  const colorClass = statusColors[status] || 'bg-gray-100 text-gray-800 border-gray-300';
  const sizeClass = sizeClasses[size];

  return (
    <span
      className={`inline-flex items-center justify-center rounded-full font-medium border ${colorClass} ${sizeClass}`}
    >
      {label}
    </span>
  );
}

export default memo(StatusBadge);
