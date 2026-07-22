import { AlertTriangle, FileText, Calendar, Package, CreditCard, Clock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from '../../i18n/useTranslation';
import type { Alert } from '../../types/dashboard';

interface AlertsPanelProps {
  alerts: Alert[];
}

const alertIcons = {
  quotation_waiting: FileText,
  measurement_overdue: Calendar,
  manufacturing_delayed: Package,
  installation_overdue: Clock,
  payment_overdue: CreditCard,
  job_inactive: AlertTriangle,
};

const severityColors = {
  critical: 'bg-red-100 border-red-500 text-red-800',
  warning: 'bg-yellow-100 border-yellow-500 text-yellow-800',
  info: 'bg-blue-100 border-blue-500 text-blue-800',
};

export default function AlertsPanel({ alerts }: AlertsPanelProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const handleAlertClick = (alert: Alert) => {
    // Navigate to the related entity
    if (alert.entity_type === 'job') {
      navigate(`/jobs/${alert.entity_id}`);
    } else if (alert.entity_type === 'quotation') {
      navigate(`/projects/${alert.entity_id}`);
    } else if (alert.entity_type === 'payment') {
      navigate(`/payments`);
    }
  };

  // Show top 10 alerts
  const displayedAlerts = alerts.slice(0, 10);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">{t('dashboard.alerts.title')}</h2>
        {alerts.length > 10 && (
          <button className="text-sm text-blue-600 hover:text-blue-800">
            {t('dashboard.alerts.viewAll')} ({alerts.length})
          </button>
        )}
      </div>

      {displayedAlerts.length === 0 ? (
        <div className="text-center text-gray-500 py-8">
          <AlertTriangle className="w-12 h-12 mx-auto mb-2 text-gray-400" />
          <p>{t('dashboard.alerts.noAlerts')}</p>
        </div>
      ) : (
        <div className="space-y-3">
          {displayedAlerts.map((alert) => {
            const Icon = alertIcons[alert.type as keyof typeof alertIcons] || AlertTriangle;
            const severityClass = severityColors[alert.severity];

            return (
              <div
                key={alert.id}
                className={`${severityClass} border-l-4 p-3 rounded cursor-pointer hover:opacity-80 transition-opacity`}
                onClick={() => handleAlertClick(alert)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    handleAlertClick(alert);
                  }
                }}
              >
                <div className="flex items-start">
                  <Icon className="w-5 h-5 ml-2 mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <h4 className="font-medium text-sm">{alert.title}</h4>
                    <p className="text-sm mt-1">{alert.description}</p>
                    {alert.days_overdue > 0 && (
                      <p className="text-xs mt-1 font-medium">
                        {alert.days_overdue} {t('common.days')} {t('dashboard.jobCard.overdue')}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
