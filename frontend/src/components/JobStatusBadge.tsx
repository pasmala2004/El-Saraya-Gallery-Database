import Badge from './Badge';
import { useTranslation } from '../i18n/useTranslation';
import type { JobStatus } from '../types';

interface JobStatusBadgeProps {
  status: JobStatus;
}

export default function JobStatusBadge({ status }: JobStatusBadgeProps) {
  const { t } = useTranslation();

  const variantMap: Record<JobStatus, 'default' | 'success' | 'warning' | 'danger' | 'info'> = {
    pending: 'default',
    measuring: 'info',
    in_production: 'warning',
    ready_for_installation: 'info',
    installed: 'success',
    completed: 'success',
    cancelled: 'danger',
  };

  return (
    <Badge variant={variantMap[status]}>
      {t(`jobStatus.${status}`)}
    </Badge>
  );
}
