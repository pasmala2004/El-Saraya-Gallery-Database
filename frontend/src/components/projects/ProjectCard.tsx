import { memo } from 'react';
import { Calendar, Clock, MoreVertical, Ruler, Wrench } from 'lucide-react';
import type { Job, Quotation, Customer, Payment } from '../../types';
import { formatCurrency, formatDate } from '../../utils/formatters';
import { useTranslation } from '../../i18n/useTranslation';
import StatusBadge from './StatusBadge';
import ProgressBar from './ProgressBar';

interface ProjectCardProps {
  job: Job;
  quotation: Quotation;
  customer: Customer;
  payments: Payment[];
  onView: (jobId: string) => void;
}

// Calculate days in current stage based on job dates
function calculateDaysInStage(job: Job): number {
  const now = new Date();
  let stageStartDate: Date;

  // Determine stage start date based on status
  if (job.status === 'measuring' && job.created_at) {
    stageStartDate = new Date(job.created_at);
  } else if (job.status === 'in_production' && job.production_start) {
    stageStartDate = new Date(job.production_start);
  } else if (job.status === 'ready_for_installation' && job.production_end) {
    stageStartDate = new Date(job.production_end);
  } else if (job.status === 'installed' && job.installation_date) {
    stageStartDate = new Date(job.installation_date);
  } else {
    stageStartDate = new Date(job.updated_at || job.created_at);
  }

  const diffTime = Math.abs(now.getTime() - stageStartDate.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
}

// Check if project is overdue
function isOverdue(job: Job): boolean {
  if (job.status === 'completed' || job.status === 'cancelled') return false;
  
  if (job.delivery_date) {
    const deliveryDate = new Date(job.delivery_date);
    const now = new Date();
    return deliveryDate < now;
  }
  
  return false;
}

// Get priority color for border
function getPriorityBorderColor(priority: string): string {
  switch (priority) {
    case 'high':
      return 'border-l-red-500';
    case 'medium':
      return 'border-l-orange-500';
    case 'low':
      return 'border-l-green-500';
    default:
      return 'border-l-gray-300';
  }
}

// Get status for completed project
function getProjectStatus(job: Job): 'completed' | 'active' {
  return job.status === 'completed' || job.status === 'cancelled' ? 'completed' : 'active';
}

function ProjectCard({ job, quotation, customer, payments, onView }: ProjectCardProps) {
  const { t } = useTranslation();
  
  // Calculate payment progress
  const totalPaid = payments
    .filter(p => p.status === 'paid')
    .reduce((sum, p) => sum + parseFloat(p.amount), 0);
  const quotationTotal = parseFloat(quotation.final_price);
  const remaining = quotationTotal - totalPaid;
  
  // Check for overdue payments
  const hasOverduePayments = payments.some(
    p => p.status === 'pending' && p.due_date && new Date(p.due_date) < new Date()
  );
  
  const daysInStage = calculateDaysInStage(job);
  const projectOverdue = isOverdue(job);
  const priorityBorder = getPriorityBorderColor(job.status === 'completed' ? 'completed' : 'high'); // TODO: Add priority field
  const isCompleted = getProjectStatus(job) === 'completed';

  return (
    <div
      className={`bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer border-l-4 ${priorityBorder} ${
        isCompleted ? 'opacity-75' : ''
      }`}
      onClick={() => onView(job.id)}
    >
      {/* Card Header */}
      <div className="px-4 py-3 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
        <div className="flex items-center gap-2 flex-wrap">
          <h3 className="text-sm font-bold text-gray-900">
            {t('projects.projectNumber')} #{job.id}
          </h3>
          <span className="text-xs text-gray-500">•</span>
          <span className="text-xs text-gray-600 font-medium">
            {quotation.quotation_number}
          </span>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            // TODO: Open more menu
          }}
          className="p-1 hover:bg-gray-200 rounded transition-colors"
        >
          <MoreVertical className="w-4 h-4 text-gray-500" />
        </button>
      </div>

      {/* Card Body */}
      <div className="p-4 space-y-3">
        {/* Customer Name */}
        <div>
          <h2 className="text-lg font-bold text-gray-900 truncate">
            {customer.full_name}
          </h2>
        </div>

        {/* Status and Priority */}
        <div className="flex items-center gap-2 flex-wrap">
          <StatusBadge
            status={job.status}
            label={t(`jobStatus.${job.status}`)}
            size="sm"
          />
          {/* TODO: Add priority field to job */}
          {projectOverdue && (
            <span className="text-xs px-2 py-0.5 bg-red-100 text-red-800 border border-red-300 rounded-full font-medium">
              {t('projectCard.overdue')}
            </span>
          )}
          {hasOverduePayments && (
            <span className="text-xs px-2 py-0.5 bg-yellow-100 text-yellow-800 border border-yellow-300 rounded-full font-medium">
              {t('payments.paymentDue')}
            </span>
          )}
        </div>

        {/* Financial Summary */}
        <div className="space-y-2 pt-2 border-t border-gray-100">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">{t('quotations.finalPrice')}:</span>
            <span className="font-semibold text-gray-900">{formatCurrency(quotationTotal)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">{t('payments.paid')}:</span>
            <span className="font-semibold text-green-600">{formatCurrency(totalPaid)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">{t('payments.remaining')}:</span>
            <span className={`font-semibold ${remaining > 0 ? 'text-red-600' : 'text-green-600'}`}>
              {formatCurrency(remaining)}
            </span>
          </div>
          <ProgressBar
            current={totalPaid}
            total={quotationTotal}
            label={t('projectCard.paymentProgress')}
          />
        </div>

        {/* Metadata */}
        <div className="grid grid-cols-2 gap-2 pt-2 border-t border-gray-100 text-xs">
          <div className="flex items-center gap-1 text-gray-600">
            <Clock className="w-3.5 h-3.5" />
            <span>{daysInStage} {t('common.days')}</span>
          </div>
          {job.measurement_date && (
            <div className="flex items-center gap-1 text-gray-600">
              <Ruler className="w-3.5 h-3.5" />
              <span>{t('projectCard.measurement')}</span>
            </div>
          )}
          {job.installation_date && (
            <div className="flex items-center gap-1 text-gray-600">
              <Wrench className="w-3.5 h-3.5" />
              <span>{t('projectCard.installation')}</span>
            </div>
          )}
          {job.delivery_date && (
            <div className="flex items-center gap-1 text-gray-600">
              <Calendar className="w-3.5 h-3.5" />
              <span>{formatDate(job.delivery_date)}</span>
            </div>
          )}
        </div>

        {/* Dates */}
        <div className="flex justify-between text-xs text-gray-500 pt-2 border-t border-gray-100">
          <span>{t('common.createdAt')}: {formatDate(job.created_at)}</span>
          {job.delivery_date && (
            <span>{t('projects.deliveryDate')}: {formatDate(job.delivery_date)}</span>
          )}
        </div>
      </div>

      {/* Card Footer */}
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-100 flex justify-end">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onView(job.id);
          }}
          className="text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
        >
          {t('common.view')} →
        </button>
      </div>
    </div>
  );
}

export default memo(ProjectCard);
