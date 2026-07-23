import { useDraggable } from '@dnd-kit/core';
import { User, Clock, Calendar, AlertCircle, DollarSign } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from '../../i18n/useTranslation';
import type { JobPipelineCard as JobCard } from '../../types/dashboard';

interface DraggableJobCardProps {
  data: JobCard;
}

const priorityColors = {
  high: 'border-t-red-500',
  medium: 'border-t-yellow-500',
  low: 'border-t-green-500',
};

export default function DraggableJobCard({ data }: DraggableJobCardProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    isDragging,
  } = useDraggable({ id: data.job_id });

  const style = transform ? {
    transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
    opacity: isDragging ? 0.5 : 1,
    cursor: isDragging ? 'grabbing' : 'grab',
  } : {
    cursor: 'grab',
  };

  const priorityClass = priorityColors[data.priority];
  const paymentPercentage = parseFloat(data.payment_progress.percentage);
  const totalAmount = parseFloat(data.payment_progress.total);
  const paidAmount = parseFloat(data.payment_progress.paid);
  const remaining = totalAmount - paidAmount;

  const handleClick = (e: React.MouseEvent) => {
    if (isDragging) return;
    navigate(`/jobs/${data.job_id}`);
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className={`bg-white rounded-lg shadow-sm border-t-4 ${priorityClass} p-3 hover:shadow-md transition-shadow ${
        data.is_overdue ? 'ring-2 ring-red-500' : ''
      } ${isDragging ? 'z-50' : ''}`}
      onClick={handleClick}
    >
      {/* Job ID - PRIMARY TITLE */}
      <div className="mb-2">
        <h3 className="text-lg font-bold text-blue-600">#{data.job_number}</h3>
      </div>

      {/* Customer Name - SECONDARY */}
      <h4 className="font-medium text-gray-700 text-sm mb-2" title={data.customer_name}>
        {data.customer_name}
      </h4>

      {/* Days in Stage Badge */}
      <div className="mb-3">
        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
          {data.days_in_stage} {t('dashboard.jobCard.days')} في المرحلة
        </span>
      </div>

      {/* Financial Info */}
      <div className="space-y-1 mb-3 text-xs">
        <div className="flex justify-between text-gray-700">
          <span>{t('dashboard.jobCard.total')}:</span>
          <span className="font-semibold">{totalAmount.toLocaleString()}</span>
        </div>
        <div className="flex justify-between text-green-600">
          <span>{t('dashboard.jobCard.paid')}:</span>
          <span className="font-semibold">{paidAmount.toLocaleString()}</span>
        </div>
        <div className="flex justify-between text-red-600">
          <span>{t('dashboard.jobCard.remaining')}:</span>
          <span className="font-semibold">{remaining.toLocaleString()}</span>
        </div>
      </div>

      {/* Payment Progress Bar */}
      <div className="mb-3">
        <div className="w-full bg-gray-200 rounded-full h-1.5">
          <div
            className="bg-green-600 h-1.5 rounded-full transition-all"
            style={{ width: `${paymentPercentage}%` }}
          />
        </div>
      </div>

      {/* Dates */}
      <div className="space-y-1">
        {data.measurement_date && (
          <div className="flex items-center text-xs text-gray-600">
            <Calendar className="w-3 h-3 ml-1 flex-shrink-0" />
            <span className="truncate">{t('dashboard.jobCard.measure')}: {new Date(data.measurement_date).toLocaleDateString('ar-EG')}</span>
          </div>
        )}
        {data.installation_date && (
          <div className="flex items-center text-xs text-gray-600">
            <Calendar className="w-3 h-3 ml-1 flex-shrink-0" />
            <span className="truncate">{t('dashboard.jobCard.install')}: {new Date(data.installation_date).toLocaleDateString('ar-EG')}</span>
          </div>
        )}
      </div>

      {/* Status Badge */}
      <div className="mt-2 pt-2 border-t border-gray-100">
        <span className="text-xs text-gray-600">{data.current_status}</span>
      </div>

      {/* Last Activity */}
      <div className="flex items-center text-xs text-gray-500 mt-2">
        <Clock className="w-3 h-3 ml-1" />
        <span className="truncate">{data.last_activity}</span>
      </div>

      {/* Overdue Indicator */}
      {data.is_overdue && (
        <div className="flex items-center text-xs text-red-600 mt-2 font-medium">
          <AlertCircle className="w-3 h-3 ml-1" />
          <span>{t('dashboard.jobCard.overdue')}</span>
        </div>
      )}
    </div>
  );
}
