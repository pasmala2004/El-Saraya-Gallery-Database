import { memo } from 'react';
import { ArrowLeft, Printer, MoreHorizontal } from 'lucide-react';
import type { Job, Quotation, Customer, Payment } from '../../types';
import Button from '../Button';
import ProjectIdentity from './ProjectIdentity';
import CustomerSummary from './CustomerSummary';
import FinancialSummary from './FinancialSummary';
import WorkflowSummary from './WorkflowSummary';
import QuickActions from './QuickActions';

interface ProjectHeaderProps {
  job: Job | null;
  quotation: Quotation;
  customer: Customer;
  payments: Payment[];
  onBack: () => void;
  onPrint: () => void;
  onAddMeasurement?: () => void;
  onAddPayment?: () => void;
  onApproveQuotation?: () => void;
  onRejectQuotation?: () => void;
  onChangeStatus?: () => void;
}

function ProjectHeader({
  job,
  quotation,
  customer,
  payments,
  onBack,
  onPrint,
  onAddMeasurement,
  onAddPayment,
  onApproveQuotation,
  onRejectQuotation,
  onChangeStatus,
}: ProjectHeaderProps) {
  const hasJob = !!job;

  return (
    <div className="sticky top-0 z-40 bg-white border-b border-gray-200 shadow-md">
      <div className="px-6 py-4 space-y-4">
        {/* Row 1: Identity - Back Button + Project IDs + Actions */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="sm"
              onClick={onBack}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="hidden sm:inline">رجوع إلى المشاريع</span>
            </Button>
            
            <ProjectIdentity
              quotationNumber={quotation.quotation_number}
              jobId={job?.id}
            />
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={onPrint}
              className="flex items-center gap-2"
            >
              <Printer className="w-4 h-4" />
              <span className="hidden sm:inline">طباعة</span>
            </Button>
            <Button variant="ghost" size="sm" className="flex items-center gap-2">
              <MoreHorizontal className="w-4 h-4" />
              <span className="hidden sm:inline">المزيد</span>
            </Button>
          </div>
        </div>

        {/* Row 2: Customer + Financial Summary */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-3 border-b border-gray-100">
          <CustomerSummary customer={customer} />
          
          <FinancialSummary
            quotation={quotation}
            payments={payments}
          />
        </div>

        {/* Row 3: Workflow Summary (Only if job exists) */}
        {hasJob && job && (
          <div className="pb-3 border-b border-gray-100">
            <WorkflowSummary
              job={job}
              quotation={quotation}
              payments={payments}
            />
          </div>
        )}

        {/* Row 4: Quick Actions */}
        <div className="flex flex-wrap items-center gap-2 pb-2">
          <QuickActions
            job={job}
            quotation={quotation}
            onAddMeasurement={onAddMeasurement}
            onAddPayment={onAddPayment}
            onApproveQuotation={onApproveQuotation}
            onRejectQuotation={onRejectQuotation}
            onChangeStatus={onChangeStatus}
          />
        </div>
      </div>
    </div>
  );
}

export default memo(ProjectHeader);
