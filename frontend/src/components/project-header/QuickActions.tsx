import { memo } from 'react';
import { Plus, Check, X, Edit } from 'lucide-react';
import type { Job, Quotation } from '../../types';
import Button from '../Button';
import { useTranslation } from '../../i18n/useTranslation';

interface QuickActionsProps {
  job: Job | null;
  quotation: Quotation;
  onAddMeasurement?: () => void;
  onAddPayment?: () => void;
  onApproveQuotation?: () => void;
  onRejectQuotation?: () => void;
  onChangeStatus?: () => void;
}

function QuickActions({
  job,
  quotation,
  onAddMeasurement,
  onAddPayment,
  onApproveQuotation,
  onRejectQuotation,
  onChangeStatus,
}: QuickActionsProps) {
  const { t } = useTranslation();
  const hasJob = !!job;

  // Determine which actions to show based on context
  const showApproveReject = !hasJob && 
    quotation.status !== 'approved' && 
    quotation.status !== 'rejected';

  const canAddMeasurement = hasJob && job.status !== 'completed' && job.status !== 'cancelled';
  const canAddPayment = hasJob && job.status !== 'completed' && job.status !== 'cancelled';

  return (
    <>
      {/* Quotation Actions (no job yet) */}
      {showApproveReject && (
        <>
          <Button
            onClick={onApproveQuotation}
            size="sm"
            variant="primary"
            className="flex items-center gap-2"
          >
            <Check className="w-4 h-4" />
            {t('projects.approve')}
          </Button>
          <Button
            onClick={onRejectQuotation}
            size="sm"
            variant="outline"
            className="flex items-center gap-2 text-red-600 border-red-300 hover:bg-red-50"
          >
            <X className="w-4 h-4" />
            {t('projects.reject')}
          </Button>
        </>
      )}

      {/* Job Actions */}
      {canAddMeasurement && onAddMeasurement && (
        <Button
          onClick={onAddMeasurement}
          size="sm"
          variant="primary"
          className="flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">{t('projects.addMeasurement')}</span>
          <span className="sm:hidden">قياس</span>
        </Button>
      )}

      {canAddPayment && onAddPayment && (
        <Button
          onClick={onAddPayment}
          size="sm"
          variant="primary"
          className="flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">{t('payments.addPayment')}</span>
          <span className="sm:hidden">دفعة</span>
        </Button>
      )}

      {/* Change Status (always available) */}
      {onChangeStatus && (
        <Button
          onClick={onChangeStatus}
          size="sm"
          variant="outline"
          className="flex items-center gap-2"
        >
          <Edit className="w-4 h-4" />
          <span className="hidden sm:inline">{t('projects.changeStatus')}</span>
          <span className="sm:hidden">الحالة</span>
        </Button>
      )}
    </>
  );
}

export default memo(QuickActions);
