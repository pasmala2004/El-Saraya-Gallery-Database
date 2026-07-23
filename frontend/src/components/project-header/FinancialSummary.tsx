import { memo, useMemo } from 'react';
import { DollarSign, TrendingUp, TrendingDown, Clock } from 'lucide-react';
import type { Quotation, Payment } from '../../types';
import { formatCurrency } from '../../utils/formatters';
import ProgressBar from '../projects/ProgressBar';

interface FinancialSummaryProps {
  quotation: Quotation;
  payments: Payment[];
}

function FinancialSummary({ quotation, payments }: FinancialSummaryProps) {
  const financialData = useMemo(() => {
    const total = parseFloat(quotation.final_price || '0');
    const paid = payments
      .filter(p => p.status === 'paid')
      .reduce((sum, p) => sum + parseFloat(p.amount), 0);
    const remaining = total - paid;
    const progress = total > 0 ? (paid / total) * 100 : 0;
    
    // Check for overdue payments
    const hasOverduePayments = payments.some(p =>
      p.status === 'pending' &&
      p.due_date &&
      new Date(p.due_date) < new Date()
    );

    // Get most recent payment date
    const lastPayment = payments
      .filter(p => p.paid_date)
      .sort((a, b) => new Date(b.paid_date!).getTime() - new Date(a.paid_date!).getTime())[0];

    return {
      total,
      paid,
      remaining,
      progress,
      hasOverduePayments,
      lastPaymentDate: lastPayment?.paid_date,
    };
  }, [quotation, payments]);

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {/* Total Value */}
      <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3 border border-blue-200">
        <div className="flex items-center gap-2 mb-1">
          <DollarSign className="w-4 h-4 text-blue-600" />
          <span className="text-xs font-medium text-blue-700">إجمالي القيمة</span>
        </div>
        <div className="text-lg font-bold text-blue-900">
          {formatCurrency(financialData.total)}
        </div>
      </div>

      {/* Paid Amount */}
      <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-3 border border-green-200">
        <div className="flex items-center gap-2 mb-1">
          <TrendingUp className="w-4 h-4 text-green-600" />
          <span className="text-xs font-medium text-green-700">مدفوع</span>
        </div>
        <div className="text-lg font-bold text-green-900">
          {formatCurrency(financialData.paid)}
        </div>
      </div>

      {/* Remaining Balance */}
      <div className={`rounded-lg p-3 border ${
        financialData.remaining > 0
          ? 'bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200'
          : 'bg-gradient-to-br from-green-50 to-green-100 border-green-200'
      }`}>
        <div className="flex items-center gap-2 mb-1">
          <TrendingDown className={`w-4 h-4 ${
            financialData.remaining > 0 ? 'text-orange-600' : 'text-green-600'
          }`} />
          <span className={`text-xs font-medium ${
            financialData.remaining > 0 ? 'text-orange-700' : 'text-green-700'
          }`}>
            متبقي
          </span>
        </div>
        <div className={`text-lg font-bold ${
          financialData.remaining > 0 ? 'text-orange-900' : 'text-green-900'
        }`}>
          {formatCurrency(financialData.remaining)}
        </div>
        {financialData.hasOverduePayments && (
          <div className="mt-1 text-xs text-red-600 font-medium flex items-center gap-1">
            <Clock className="w-3 h-3" />
            دفعة متأخرة
          </div>
        )}
      </div>

      {/* Payment Progress */}
      <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-3 border border-purple-200">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-purple-700">التقدم</span>
          <span className="text-xs font-bold text-purple-900">
            {financialData.progress.toFixed(0)}%
          </span>
        </div>
        <ProgressBar
          current={financialData.paid}
          total={financialData.total}
          showPercentage={false}
        />
        {financialData.lastPaymentDate && (
          <div className="mt-2 text-xs text-purple-600">
            آخر دفعة: {new Date(financialData.lastPaymentDate).toLocaleDateString('ar-EG', {
              month: 'short',
              day: 'numeric'
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default memo(FinancialSummary);
