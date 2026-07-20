import Badge from './Badge';
import { useTranslation } from '../i18n/useTranslation';
import type { PaymentStatus } from '../types';

interface PaymentStatusBadgeProps {
  status: PaymentStatus;
}

export default function PaymentStatusBadge({ status }: PaymentStatusBadgeProps) {
  const { t } = useTranslation();

  const variantMap: Record<PaymentStatus, 'default' | 'success' | 'warning' | 'danger' | 'info'> = {
    pending: 'default',
    paid: 'success',
    overdue: 'danger',
    cancelled: 'danger',
  };

  return (
    <Badge variant={variantMap[status]}>
      {t(`paymentStatus.${status}`)}
    </Badge>
  );
}
